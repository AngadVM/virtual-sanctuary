from flask import (
        Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from Blog.auth import login_required
from Blog.db import get_db
import os

bp = Blueprint('blog', __name__)


# Adding helper func
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, image_url, created, author_id, username '  
        ' FROM post p JOIN user u ON p.author_id = u.id '
        ' ORDER BY created DESC'  
    ).fetchall()
    return render_template('blog/index.html', posts=posts)




@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        image_url = None  # Initialize image_url

        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(current_app.static_folder, 'uploads')
                os.makedirs(upload_folder, exist_ok=True)  # Ensure directory exists
                file.save(os.path.join(upload_folder, filename))
                image_url = f'uploads/{filename}'  # Store the file path

        if not title:
            error = 'Title is required.'

        if error:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, image_url, author_id)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, image_url, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')



def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, image_url, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        # Handle image update
        if 'image' not in request.files:
            image_url = post['image_url']  # Keep existing image
        else:
            file = request.files['image']
            if file.filename == '':
                image_url = post['image_url']  # Keep existing image
            elif file and allowed_file(file.filename):
                # Delete old image if it exists
                if post['image_url']:
                    old_image_path = os.path.join(current_app.static_folder, post['image_url'])
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                filename = secure_filename(file.filename)
                os.makedirs(os.path.join(current_app.static_folder, 'uploads'), exist_ok=True)
                file.save(os.path.join(current_app.static_folder, 'uploads', filename))
                image_url = f'uploads/{filename}'
            else:
                error = 'Invalid file type. Allowed types are png, jpg, jpeg, gif'

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?, image_url = ?'
                ' WHERE id = ?',
                (title, body, image_url, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)



@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    # Delete the image file if it exists
    if post['image_url']:
        image_path = os.path.join(current_app.static_folder, post['image_url'])
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
