import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
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

# For development only -- remove in production!
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

# Blueprint for auth
bp = Blueprint('auth', __name__, url_prefix='/auth')


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
        """
        Verify if the social media handle actually exists.
        Uses caching to prevent excessive API calls.
        """
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
            return True  # On error, assume handle exists to avoid blocking valid users



# Add Google login routes
@bp.route('/google-login')
def google_login():
    # Find out what URL to hit for Google login
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)



@bp.route('/google-login/callback')
def google_callback():
    try:
        # Get authorization code Google sent back
        code = request.args.get("code")
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]

        # Prepare and send request to get tokens
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

        # Parse the tokens
        client.parse_request_body_response(json.dumps(token_response.json()))
        
        # Get user info from Google
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)

        if userinfo_response.json().get("email_verified"):
            google_id = userinfo_response.json()["sub"]
            email = userinfo_response.json()["email"]
            username = userinfo_response.json().get("given_name", email.split('@')[0])
        else:
            flash("Google authentication failed - Email not verified", "error")
            return redirect(url_for("auth.login"))

        # Check if user exists and handle accordingly
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()

        if user is None:
            try:
                # Create new user
                google_password = os.urandom(24).hex()
                db.execute(
                    "INSERT INTO user (email, username, password, google_id) VALUES (?, ?, ?, ?)",
                    (email, username, generate_password_hash(google_password), google_id)
                )
                db.commit()
                user = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()
                flash('Account created successfully!', 'success')
            except db.IntegrityError as e:
                flash('Error creating account. Please try again.', 'error')
                return redirect(url_for("auth.login"))

        # Log in the user
        session.clear()
        session['user_id'] = user['id']
        return redirect(url_for('index'))

    except Exception as e:
        flash(f"Authentication error: {str(e)}", "error")
        return redirect(url_for("auth.login"))



# Modify existing register route to handle both traditional and Google sign-up
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        email = request.form['email'].strip().lower()
        db = get_db()
        error = None

        # Input validation
        if not username:
            error = 'Username is required'
        elif len(username) < 3:
            error = 'Username must be at least 3 characters long'
        elif not password:
            error = 'Password is required'
        elif not validate_password(password):
            error = 'Password must be at least 8 characters and contain uppercase, lowercase, and numbers'
        elif not email:
            error = 'Email is required'
        elif not validate_email(email):
            error = 'Invalid email format'

        if error is None:
            try:
                existing_email = db.execute(
                    'SELECT id FROM user WHERE email = ?', (email,)
                ).fetchone()
                if existing_email:
                    error = 'Email already registered'
                else:
                    db.execute(
                        "INSERT INTO user (email, username, password) VALUES (?, ?, ?)",
                        (email, username, generate_password_hash(password))
                    )
                    db.commit()
                    flash('Registration successful! Please log in.', 'success')
                    return redirect(url_for("auth.login"))
            except db.IntegrityError:
                error = f"User {username} is already registered."
        flash(error, 'error')

    return render_template('auth/register.html')

# Keep the rest of your existing code...



@bp.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier'].strip() # Can be username or email
        password = request.form['password']

        db = get_db()
        error = None

        # Check if identifier is email or username
        if '@' in identifier:
            user = db.execute(
                'SELECT * FROM user WHERE email = ?', (identifier.lower(),)
            ).fetchone()
        else:
            user = db.execute(
                'SELECT * FROM user WHERE username = ?', (identifier,)
            ).fetchone()

        if user is None:
            error = 'Incorrect credentials'
        elif not check_password_hash(user['password'], password):
            error = 'Invalid credentials'


        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
    
        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# Logout

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# to check if user is logged in before crud operations are performed on the post

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view



@bp.route('/profile/<int:user_id>')
@bp.route('/profile', defaults={'user_id': None})
@login_required
def profile(user_id=None):
    db = get_db()
    
    if user_id is None:
        user_id = g.user['id']
        
    user = db.execute(
        'SELECT id, username, email, about, twitter_handle, instagram_handle, linkedin_url, profile_image '
        'FROM user WHERE id = ?',
        (user_id,)
    ).fetchone()
    
    if user is None:
        abort(404)
        
    is_own_profile = g.user['id'] == user_id

    posts = db.execute(
        '''SELECT p.id, title, body, created, author_id, username
           FROM post p JOIN user u ON p.author_id = u.id
           WHERE u.id = ?
           ORDER BY created DESC''',
        (user_id,)
    ).fetchall()

    return render_template('auth/profile.html', user=user, posts=posts, is_own_profile=is_own_profile)




@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    from flask import current_app
    
    db = get_db()
    user = db.execute(
        'SELECT id, username, email, about, twitter_handle, instagram_handle, linkedin_url, profile_image '
        'FROM user WHERE id = ?',
        (g.user['id'],)
    ).fetchone()

    if request.method == 'POST':
        about = request.form.get('about', '').strip()
        twitter = request.form.get('twitter_handle', '').strip()
        instagram = request.form.get('instagram_handle', '').strip()
        linkedin = request.form.get('linkedin_url', '').strip()
        
        error = None
        validator = SocialMediaValidator()

        # Validate Twitter handle
        if twitter:
            twitter = validator.clean_handle(twitter, 'twitter')
            if not validator.validate_twitter(twitter):
                error = "Invalid Twitter handle format"
            elif not validator.verify_handle_exists(twitter, 'twitter'):
                error = "Twitter handle does not exist"
            twitter = f'@{twitter}'  # Add @ prefix for storage

        # Validate Instagram handle
        if instagram:
            instagram = validator.clean_handle(instagram, 'instagram')
            if not validator.validate_instagram(instagram):
                error = "Invalid Instagram handle format"
            elif not validator.verify_handle_exists(instagram, 'instagram'):
                error = "Instagram handle does not exist"

        # Validate LinkedIn URL
        if linkedin:
            if not validator.validate_linkedin_url(linkedin):
                error = "Invalid LinkedIn URL format"
            elif not validator.verify_handle_exists(linkedin, 'linkedin'):
                error = "LinkedIn profile URL does not exist"

        # Handle profile image upload
        profile_image = user['profile_image']
        
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    try:
                        upload_folder = os.path.join(current_app.root_path, 'static', 'profile_images')
                        timestamp = int(time.time())
                        original_filename = secure_filename(file.filename)
                        filename = f"{timestamp}_{original_filename}"
                        file_path = os.path.join(upload_folder, filename)
                        
                        file.save(file_path)
                        profile_image = os.path.join('profile_images', filename)
                        
                        if user['profile_image']:
                            old_image_path = os.path.join(current_app.root_path, 'static', user['profile_image'])
                            if os.path.exists(old_image_path):
                                os.remove(old_image_path)
                                
                    except Exception as e:
                        error = f"Error saving profile image: {str(e)}"
                        print(f"File upload error: {str(e)}")
                else:
                    error = f"Invalid file type. Allowed types are: {', '.join(ALLOWED_EXTENSIONS)}"
        
        if error is None:
            try:
                db.execute(
                    '''UPDATE user 
                       SET about = ?,
                           twitter_handle = ?,
                           instagram_handle = ?,
                           linkedin_url = ?,
                           profile_image = ?
                       WHERE id = ?''',
                    (about, twitter, instagram, linkedin, profile_image, g.user['id'])
                )
                db.commit()
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('blog.index'))
            except db.Error as e:
                error = f"Error updating profile: {str(e)}"
                print(f"Database error: {str(e)}")
        
        if error:
            flash(error, 'error')

    return render_template('auth/edit_profile.html', user=user)
    return render_template('auth/edit_profile.html', user=user)

