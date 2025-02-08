import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from Blog.db import get_db
import re


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
