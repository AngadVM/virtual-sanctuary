import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from Blog.db import get_db
import re, os, time


UPLOAD_FOLDER = 'static/profile_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


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
                # Check if email already exists
                existing_email = db.execute(
                    'SELECT id FROM user WHERE email = ?', (email,)
                ).fetchone()
                if existing_email:
                    error = 'Email already registered'
                else:

                    db.execute(
                        "INSERT INTO user (email, username, password) VALUES (?, ?, ?)",
                        (email, username, generate_password_hash(password)),
                    )
                    db.commit()
                    flash('Registration successful! Please log in.', 'success')
                    return redirect(url_for("auth.login"))


            except db.IntegrityError:
                error = f"User {username} is already registered."
             
        flash(error, 'error')

    return render_template('auth/register.html')





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

        if twitter and not twitter.startswith('@'):
            twitter = f'@{twitter}'
            
        # Handle profile image upload
        profile_image = user['profile_image']  # Keep existing image by default
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to filename to make it unique
                timestamp = int(time.time())
                filename = f"{timestamp}_{filename}"
                # Create upload folder if it doesn't exist
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                # Save the file
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                # Update profile_image with the relative path
                profile_image = f'profile_images/{filename}'
                
                # Delete old profile image if it exists
                if user['profile_image']:
                    old_image_path = os.path.join('static', user['profile_image'])
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
        
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
                error = f"Error updating profile: {e}"
        
        flash(error, 'error')

    return render_template('auth/edit_profile.html', user=user)
