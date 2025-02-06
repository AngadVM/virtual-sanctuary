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
        'SELECT p.id, title, body, created, author_id, username '
        'FROM post p JOIN user u ON p.author_id = u.id '
        'ORDER BY created DESC'
    ).fetchall()
    
    # Fetch images for each post
    posts_with_images = []
    for post in posts:
        post_dict = dict(post)
        post_dict['images'] = [
            img['image_url'] for img in 
            db.execute('SELECT image_url FROM post_images WHERE post_id = ?', 
                       (post_dict['id'],)).fetchall()
        ]
        posts_with_images.append(post_dict)
    
    return render_template('blog/index.html', posts=posts_with_images)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            # Insert post first
            cursor = db.execute(
                'INSERT INTO post (title, body, author_id)'
                'VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            post_id = cursor.lastrowid

            # Handle multiple image uploads
            images = request.files.getlist('images')
            for file in images:
                if file and file.filename:
                    if allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        os.makedirs(os.path.join(current_app.static_folder, 'uploads'), exist_ok=True)
                        file_path = os.path.join(current_app.static_folder, 'uploads', filename)
                        file.save(file_path)
                        
                        # Save image path to database
                        db.execute(
                            'INSERT INTO post_images (post_id, image_url) VALUES (?, ?)',
                            (post_id, f'uploads/{filename}')
                        )
                    else:
                        flash('Invalid file type. Allowed types are png, jpg, jpeg, gif')

            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')



@bp.route('/<int:id>/view')
def get_post(id):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username '
        'FROM post p JOIN user u ON p.author_id = u.id '
        'WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    # Convert to dictionary and fetch images
    post_dict = dict(post)
    post_dict['images'] = [
        img['image_url'] for img in 
        get_db().execute('SELECT image_url FROM post_images WHERE post_id = ?', 
                         (post_dict['id'],)).fetchall()
    ]

    return render_template('blog/view.html', post=post_dict)



@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    # Retrieve the post
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    # Retrieve existing images
    images = get_db().execute(
        'SELECT image_url FROM post_images WHERE post_id = ?',
        (id,)
    ).fetchall()

    # Check if post exists and if current user is the author
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")
    
    if post['author_id'] != g.user['id']:
        abort(403)

    # Convert Row to dictionary
    post = dict(post)
    images = [dict(img)['image_url'] for img in images]

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        # Handle image removal
        removed_images = request.form.getlist('remove_images')
        
        # Handle new image uploads
        uploaded_images = request.files.getlist('images')

        # Validate title
        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            
            # Remove selected images
            for img in removed_images:
                # Remove from filesystem
                img_path = os.path.join(current_app.static_folder, img)
                if os.path.exists(img_path):
                    os.remove(img_path)
                
                # Remove from database
                db.execute('DELETE FROM post_images WHERE image_url = ?', (img,))

            # Handle new image uploads
            for file in uploaded_images:
                if file and file.filename:
                    if allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        os.makedirs(os.path.join(current_app.static_folder, 'uploads'), exist_ok=True)
                        file_path = os.path.join(current_app.static_folder, 'uploads', filename)
                        file.save(file_path)
                        
                        # Save image path to database
                        db.execute(
                            'INSERT INTO post_images (post_id, image_url) VALUES (?, ?)',
                            (id, f'uploads/{filename}')
                        )
                    else:
                        flash('Invalid file type. Allowed types are png, jpg, jpeg, gif')

            # Update post details
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
    
    return render_template('blog/update.html', post=post, images=images)




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
