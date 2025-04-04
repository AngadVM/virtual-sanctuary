import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from Blog.db import get_db
import re, os, time, requests
from functools import lru_cache
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from oauthlib.oauth2 import WebApplicationClient
import json


UPLOAD_FOLDER = os.path.join('static', 'profile_images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# For development only 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

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
    pattern =r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern,email) is not None


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
        """Validate Twitter handle format"""
        pattern = r'^[A-Za-z0-9_]{4,15}$'
        return bool(re.match(pattern, handle)) and not handle.isdigit()

    @staticmethod
    def validate_instagram(handle):
        """Validate Instagram handle format"""
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
        """Validate LinkedIn URL format"""
        pattern = r'^(https?:\/\/)?(www\.)?linkedin\.com\/in\/[a-zA-Z0-9\-]{3,100}\/?$'
        return bool(re.match(pattern, url))

    @staticmethod
    @lru_cache(maxsize=100)
    def verify_handle_exists(handle, platform):
        """Verify if the social media handle actually exists"""
        try:
            if platform == 'twitter':
                url = f"https://twitter.com/{handle}"
            elif platform == 'instagram':
                url = f"https://www.instagram.com/{handle}"
            elif platform == 'linkedin':
                url = handle
            
            response = requests.head(url, allow_redirects=True, timeout=5)
            return response.status_code == 200
        except:
            return True


@bp.route('/google-login')
def google_login():
    """Initiate Google OAuth login"""
    try:
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=request.base_url + "/callback",
            scope=["openid", "email", "profile"],
        )
        return jsonify({
            "success": True,
            "auth_url": request_uri
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to initialize Google login: {str(e)}"
        }), 500


@bp.route('/google-login/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        code = request.args.get("code")
        if not code:
            return jsonify({
                "success": False,
                "error": "No authorization code received"
            }), 400

        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]

        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=request.base_url,
            code=code
        )

        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )

        client.parse_request_body_response(json.dumps(token_response.json()))
        
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)

        if not userinfo_response.json().get("email_verified"):
            return jsonify({
                "success": False,
                "error": "Email not verified by Google"
            }), 400

        google_id = userinfo_response.json()["sub"]
        email = userinfo_response.json()["email"]
        username = userinfo_response.json().get("given_name", email.split('@')[0])

        db = get_db()
        user = db.execute(
            'SELECT * FROM user WHERE email = ?', (email,)
        ).fetchone()

        if user is None:
            # Create new user
            db.execute(
                'INSERT INTO user (username, email, google_id) VALUES (?, ?, ?)',
                (username, email, google_id)
            )
            db.commit()
            user = db.execute(
                'SELECT * FROM user WHERE email = ?', (email,)
            ).fetchone()

        session.clear()
        session['user_id'] = user['id']

        return jsonify({
            "success": True,
            "message": "Successfully logged in with Google",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email']
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Google authentication failed: {str(e)}"
        }), 500


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'
        elif not validate_email(email):
            error = 'Invalid email format.'
        elif not validate_password(password):
            error = 'Password must be at least 8 characters long and contain uppercase, lowercase, and numbers.'
        elif db.execute('SELECT id FROM user WHERE username = ?', (username,)).fetchone() is not None:
            error = f"User {username} is already registered."
        elif db.execute('SELECT id FROM user WHERE email = ?', (email,)).fetchone() is not None:
            error = f"Email {email} is already registered."

        if error is not None:
            return jsonify({
                "success": False,
                "error": error
            }), 400

        try:
            db.execute(
                'INSERT INTO user (username, password, email) VALUES (?, ?, ?)',
                (username, generate_password_hash(password), email)
            )
            db.commit()

            return jsonify({
                "success": True,
                "message": "Registration successful",
                "user": {
                    "username": username,
                    "email": email
                }
            })

        except Exception as e:
            db.rollback()
            return jsonify({
                "success": False,
                "error": f"Registration failed: {str(e)}"
            }), 500

    return jsonify({
        "success": True,
        "message": "Registration form endpoint"
    })


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is not None:
            return jsonify({
                "success": False,
                "error": error
            }), 401

        session.clear()
        session['user_id'] = user['id']

        return jsonify({
            "success": True,
            "message": "Successfully logged in",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email']
            }
        })

    return jsonify({
        "success": True,
        "message": "Login form endpoint"
    })


@bp.before_app_request
def load_logged_in_user():
    """Load logged in user before each request"""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    return jsonify({
        "success": True,
        "message": "Successfully logged out"
    })


def login_required(view):
    """Decorator to require login for routes"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return jsonify({
                "success": False,
                "error": "Login required"
            }), 401
        return view(**kwargs)
    return wrapped_view


@bp.route('/profile/<int:user_id>')
@bp.route('/profile', defaults={'user_id': None})
@login_required
def profile(user_id=None):
    """Get user profile"""
    if user_id is None:
        user_id = g.user['id']

    db = get_db()
    user = db.execute(
        'SELECT u.*, COUNT(DISTINCT p.id) as post_count, COUNT(DISTINCT c.id) as comment_count'
        ' FROM user u'
        ' LEFT JOIN post p ON u.id = p.author_id'
        ' LEFT JOIN comment c ON u.id = c.author_id'
        ' WHERE u.id = ?'
        ' GROUP BY u.id',
        (user_id,)
    ).fetchone()

    if user is None:
        return jsonify({
            "success": False,
            "error": "User not found"
        }), 404

    # Convert SQLite Row to dictionary
    user_dict = dict(user)

    return jsonify({
        "success": True,
        "user": {
            "id": user_dict['id'],
            "username": user_dict['username'],
            "email": user_dict['email'],
            "bio": user_dict.get('bio'),
            "profile_image": user_dict.get('profile_image'),
            "social_media": {
                "twitter": user_dict.get('twitter_handle'),
                "instagram": user_dict.get('instagram_handle'),
                "linkedin": user_dict.get('linkedin_url')
            },
            "stats": {
                "posts": user_dict['post_count'],
                "comments": user_dict['comment_count']
            }
        }
    })


@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        bio = request.form.get('bio', '').strip()
        twitter = request.form.get('twitter', '').strip()
        instagram = request.form.get('instagram', '').strip()
        linkedin = request.form.get('linkedin', '').strip()
        
        error = None
        validator = SocialMediaValidator()

        # Validate social media handles
        if twitter and not validator.validate_twitter(validator.clean_handle(twitter, 'twitter')):
            error = 'Invalid Twitter handle'
        if instagram and not validator.validate_instagram(validator.clean_handle(instagram, 'instagram')):
            error = 'Invalid Instagram handle'
        if linkedin and not validator.validate_linkedin_url(linkedin):
            error = 'Invalid LinkedIn URL'

        if error is not None:
            return jsonify({
                "success": False,
                "error": error
            }), 400

        db = get_db()
        try:
            # Handle profile image upload
            profile_image = None
            if 'profile_image' in request.files:
                file = request.files['profile_image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    upload_folder = os.path.join(current_app.static_folder, UPLOAD_FOLDER)
                    os.makedirs(upload_folder, exist_ok=True)
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    profile_image = os.path.join(UPLOAD_FOLDER, filename)

            # Update user profile
            if profile_image:
                db.execute(
                    'UPDATE user SET bio = ?, twitter_handle = ?, instagram_handle = ?, '
                    'linkedin_url = ?, profile_image = ? WHERE id = ?',
                    (bio, twitter, instagram, linkedin, profile_image, g.user['id'])
                )
            else:
                db.execute(
                    'UPDATE user SET bio = ?, twitter_handle = ?, instagram_handle = ?, '
                    'linkedin_url = ? WHERE id = ?',
                    (bio, twitter, instagram, linkedin, g.user['id'])
                )
            db.commit()

            return jsonify({
                "success": True,
                "message": "Profile updated successfully",
                "profile": {
                    "bio": bio,
                    "twitter": twitter,
                    "instagram": instagram,
                    "linkedin": linkedin,
                    "profile_image": profile_image
                }
            })

        except Exception as e:
            db.rollback()
            return jsonify({
                "success": False,
                "error": f"Failed to update profile: {str(e)}"
            }), 500

    return jsonify({
        "success": True,
        "message": "Profile edit form endpoint"
    })
