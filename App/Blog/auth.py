import functools, json, os, time, requests, re
from functools import lru_cache, wraps
from dotenv import load_dotenv
from flask import Blueprint, redirect, request, url_for, jsonify, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from Blog.db import get_db
from oauthlib.oauth2 import WebApplicationClient
from flask_login import UserMixin
from Blog import login_manager
import random

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    @staticmethod
    def get(user_id):
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
        if user:
            return User(user['id'], user['username'], user['email'])
        return None

    def get_id(self):
        return str(self.id)



PROFILE_IMAGE_FOLDER = os.path.join('static', 'profile_images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# For development only 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

load_dotenv()
# Google OAuth2 config
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Blueprint for auth
bp = Blueprint('auth', __name__, url_prefix='/auth')

# Initialize OAuth2 client
client = WebApplicationClient(GOOGLE_CLIENT_ID)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_email(email):
    """Validate email format using regex pattern. """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Validate password strength:
    - At least 8 characters
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    """
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True


class SocialMediaValidator:
    @staticmethod
    def clean_handle(handle, platform):
        """Remove @ and leading/trailing whitespace from handles"""
        handle = handle.strip()
        if platform in ['twitter', 'instagram'] and handle.startswith('@'):
            handle = handle[1:]
        return handle

    @staticmethod
    def validate_twitter(handle):
        """
        Validate Twitter handle format:
        - 4-15 characters
        - Only alphanumeric and underscore
        - Cannot be only numbers
        """
        pattern = r'^[A-Za-z0-9_]{4,15}$'
        return bool(re.match(pattern, handle)) and not handle.isdigit()

    @staticmethod
    def validate_instagram(handle):
        """
        Validate Instagram handle format:
        - 1-30 characters
        - Only alphanumeric, periods, and underscores
        - Cannot start or end with period
        - Cannot have consecutive periods
        """
        pattern = r'^[A-Za-z0-9._]{1,30}$'
        if not re.match(pattern, handle):
            return False
        if handle.startswith('.') or handle.endswith('.'):
            return False
        if '..' in handle:
            return False
        return True

    @staticmethod
    def validate_linkedin_url(url):
        """
        Validate LinkedIn URL format:
        - Must start with linkedin.com/in/
        - Username portion should be 3-100 chars
        - Can contain letters, numbers, hyphens
        """
        pattern = r'^(https?:\/\/)?(www\.)?linkedin\.com\/in\/[a-zA-Z0-9\-]{3,100}\/?$'
        return bool(re.match(pattern, url))

    
    @staticmethod
    @lru_cache(maxsize=100)
    def verify_handle_exists(handle, platform):
        """Verify if a social media handle actually exists."""
        urls = {
            "twitter": f"https://twitter.com/{handle}",
            "instagram": f"https://www.instagram.com/{handle}",
            "linkedin": handle if handle.startswith("https://www.linkedin.com/in/") else None
        }

        url = urls.get(platform)
        if not url:
            return False

        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            return response.status_code in [200, 301, 302]  # Allow redirects
        except requests.RequestException:
            return False  # Assume handle doesn't exist if request fails




# Google login routes

@bp.route('/google-login')
def google_login():
    try:
        # Ensure GOOGLE_CLIENT_ID is available
        if not GOOGLE_CLIENT_ID:
            return jsonify({"status": "error", "message": "Google OAuth Client ID is missing"}), 500

        # Get Google's OAuth 2.0 authorization endpoint
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg.get("authorization_endpoint")

        if not authorization_endpoint:
            return jsonify({"status": "error", "message": "Failed to retrieve Google OAuth configuration"}), 500

        # Construct request URI for Google login
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=url_for("auth.google_callback", _external=True),  
            scope=["openid", "email", "profile"],
        )

        return redirect(request_uri)

    except Exception as e:
        return jsonify({"status": "error", "message": f"OAuth login failed: {str(e)}"}), 500



 

@bp.route('/google-login/callback')
def google_callback():
    try:
        code = request.args.get("code")
        if not code:
            return jsonify({"status": "error", "message": "Missing authorization code"}), 400

        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]

        token_url, headers, body = client.prepare_token_request(
            token_endpoint, authorization_response=request.url, redirect_url=request.base_url, code=code
        )

        token_response = requests.post(
            token_url, headers=headers, data=body, auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
        )

        if token_response.status_code != 200:
            return jsonify({"status": "error", "message": "Failed to retrieve access token"}), 500

        client.parse_request_body_response(json.dumps(token_response.json()))

        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)

        user_data = userinfo_response.json()
        if not user_data.get("email_verified"):
            return jsonify({"status": "error", "message": "Email verification failed"}), 401

        email = user_data["email"]
        username = user_data.get("given_name", email.split('@')[0])

        db = get_db()
        user = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()

        if user is None:
            #  Check if username already exists and make it unique
            existing_user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
            if existing_user:
                username = f"{username}{random.randint(1000, 9999)}"  #  Append random number to make it unique

            google_password = os.urandom(24).hex()
            db.execute(
                "INSERT INTO user (email, username, password, google_id) VALUES (?, ?, ?, ?)",
                (email, username, generate_password_hash(google_password), user_data["sub"])
            )
            db.commit()
            user = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()

        user_obj = User(user['id'], user['username'], user['email'])
        login_user(user_obj)

        return jsonify({"status": "success", "message": "Login successful", "user_id": user_obj.id}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Authentication error: {str(e)}"}), 500


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)  #  Load user from database




@bp.route('/logout')
def logout():
    print(f" Logging out user: {current_user.id}")  # Debugging
    logout_user()
    return jsonify({"status": "success", "message": "Logged out successfully"}), 200




def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        print(f"🔍 DEBUG: current_user.is_authenticated = {current_user.is_authenticated}")  #  Debugging
        if not current_user.is_authenticated:
            return jsonify({"status": "error", "message": "Authentication required"}), 401
        return view(*args, **kwargs)

    return wrapped_view



@bp.route('/profile', methods=['GET'])
@login_required
def profile():
    try:
        # Debugging: Check if current_user is set
        if not current_user.is_authenticated:
            return jsonify({"status": "error", "message": "User not authenticated"}), 401

        db = get_db()
        user = db.execute(
            'SELECT id, username, email, about, twitter_handle, instagram_handle, linkedin_url, profile_image '
            'FROM user WHERE id = ?',
            (current_user.id,)
        ).fetchone()

        if user is None:
            return jsonify({"status": "error", "message": "User not found"}), 404

        user_dict = dict(user)
        user_dict.pop('password', None)

        return jsonify({
            "status": "success",
            "user": user_dict
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



@bp.route('/profile/edit', methods=['POST'])
@login_required
def edit_profile():
    db = get_db()
    user = db.execute(
        'SELECT id, username, email, about, twitter_handle, instagram_handle, linkedin_url, profile_image '
        'FROM user WHERE id = ?',
        (current_user.id,)
    ).fetchone()

    if request.method == 'GET':
        user_dict = dict(user)
        return jsonify({"status": "success", "user": user_dict}), 200

    if request.method == 'POST':
        # Parse JSON data if request is application/json
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        username = data.get('username', '').strip()
        about = data.get('about', '').strip()
        twitter = data.get('twitter_handle', '').strip()
        instagram = data.get('instagram_handle', '').strip()
        linkedin = data.get('linkedin_url', '').strip()

        error = None
        updates = {}

        # Username validation
        if username and username != user['username']:
            if len(username) < 3:
                return jsonify({"status": "error", "message": "Username must be at least 3 characters long"}), 400
            else:
                existing_user = db.execute(
                    'SELECT id FROM user WHERE username = ? AND id != ?',
                    (username, current_user.id)
                ).fetchone()
                if existing_user:
                    return jsonify({"status": "error", "message": "Username already taken"}), 400
                updates['username'] = username

        # Social media validation
        validator = SocialMediaValidator()

        if twitter:
            twitter = validator.clean_handle(twitter, 'twitter')
            if not validator.validate_twitter(twitter):
                return jsonify({"status": "error", "message": "Invalid Twitter handle format"}), 400
            updates['twitter_handle'] = f'@{twitter}'

        if instagram:
            instagram = validator.clean_handle(instagram, 'instagram')
            if not validator.validate_instagram(instagram):
                return jsonify({"status": "error", "message": "Invalid Instagram handle format"}), 400
            updates['instagram_handle'] = instagram

        if linkedin:
            if not validator.validate_linkedin_url(linkedin):
                return jsonify({"status": "error", "message": "Invalid LinkedIn URL format"}), 400
            updates['linkedin_url'] = linkedin

        # Update 'about' section
        if about and about != user['about']:
            updates['about'] = about

      
        # Profile image upload handling
        if 'profile_image' in request.files:
            file = request.files['profile_image']

            if file.filename == '':  # Check if file is empty
                return jsonify({"status": "error", "message": "No file selected"}), 400

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)

                # Ensure the upload directory exists
                profile_folder = current_app.config.get('PROFILE_IMAGE_FOLDER', 'static/profile_images')
                os.makedirs(profile_folder, exist_ok=True)

                filepath = os.path.join(profile_folder, filename)
                file.save(filepath)

                # Store relative path for easy retrieval
                updates['profile_image'] = f"/static/profile_images/{filename}"
            else:
                return jsonify({"status": "error", "message": "Invalid file format. Allowed formats: png, jpg, jpeg, gif"}), 400
         # Apply updates if there are any changes
        if updates:
            query = "UPDATE user SET " + ", ".join(f"{key} = ?" for key in updates.keys()) + " WHERE id = ?"
            values = list(updates.values()) + [current_user.id]
            db.execute(query, values)
            db.commit()

        return jsonify({"status": "success", "message": "Profile updated successfully"}), 200

