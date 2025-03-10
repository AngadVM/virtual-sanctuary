from flask import(
    Blueprint, flash, g, redirect, render_template, 
    request, url_for, current_app
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from Blog.auth import login_required
from Blog.db import get_db
import os
import bleach

bp = Blueprint('blog', __name__)

# Helper functions
def allowed_file(filename):
    """Check if a filename has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


def get_post_comments(post_id):
    """Get all comments for a specific post ordered by creation date."""
    db = get_db()
    comments = db.execute(
        'SELECT c.id, c.body, c.created, c.author_id, u.username, p.author_id as post_author_id'
        ' FROM comment c'
        ' JOIN user u ON c.author_id = u.id'
        ' JOIN post p ON c.post_id = p.id'
        ' WHERE c.post_id = ?'
        ' ORDER BY c.created DESC',
        (post_id,)
    ).fetchall()
    return comments


def get_post(id, check_author=True):
    """Get a post and its images by id."""
    post = get_db().execute(
        'SELECT p.id, p.title, p.body, p.created, p.author_id, u.username'
        ' FROM post p'
        ' JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    # Convert to dictionary and fetch images
    post_dict = dict(post)
    post_dict['images'] = [
        img['image_url'] for img in 
        get_db().execute(
            'SELECT image_url FROM post_images WHERE post_id = ?', 
            (post_dict['id'],)
        ).fetchall()
    ]

    return post_dict


# Route handlers
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
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


@bp.route('/<int:id>/view')
def view(id):
    post = get_post(id, check_author=False)
    comments = get_post_comments(id)
    return render_template('blog/view.html', post=post, comments=comments)



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
            # Sanitize HTML content while allowing specific tags
            allowed_tags = [
                'p', 'h1', 'h2', 'strong', 'em', 'u', 'blockquote', 
                'code', 'pre', 'ol', 'ul', 'li', 'a'
            ]
            allowed_attrs = {
                'a': ['href', 'title'],
                '*': ['class']
            }
            clean_body = bleach.clean(
                body,
                tags=allowed_tags,
                attributes=allowed_attrs,
                strip=True
            )

            db = get_db()
            # Insert post
            cursor = db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, clean_body, g.user['id'])
            )
            post_id = cursor.lastrowid

            # Handle multiple image uploads
            images = request.files.getlist('images')
            upload_folder = os.path.join(current_app.static_folder, 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            for file in images:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    
                    # Save image path to database
                    db.execute(
                        'INSERT INTO post_images (post_id, image_url) VALUES (?, ?)',
                        (post_id, f'uploads/{filename}')
                    )

            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            
            # Handle image removal
            removed_images = request.form.getlist('remove_images')
            for img in removed_images:
                # Remove from filesystem
                img_path = os.path.join(current_app.static_folder, img)
                if os.path.exists(img_path):
                    os.remove(img_path)
                
                # Remove from database
                db.execute('DELETE FROM post_images WHERE image_url = ?', (img,))

            # Handle new image uploads
            for file in request.files.getlist('images'):
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
    
    return render_template('blog/update.html', post=post, images=post['images'])

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    db = get_db()
    
    try:
        # Delete physical image files
        for image_url in post['images']:
            try:
                image_path = os.path.join(current_app.static_folder, image_url)
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"Error deleting image file: {e}")
        
        # Delete image records and post from database
        db.execute('DELETE FROM post_images WHERE post_id = ?', (id,))
        db.execute('DELETE FROM post WHERE id = ?', (id,))
        db.commit()
        
        flash('Post was successfully deleted.')
    except Exception as e:
        db.rollback()
        flash('Error deleting post.')
        print(f"Database error: {e}")
        
    return redirect(url_for('blog.index'))

@bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    body = request.form.get('body', '').strip()
    error = None

    if not body:
        error = 'Comment cannot be empty.'
    
    if error is not None:
        flash(error)
    else:
        db = get_db()
        post = db.execute('SELECT id FROM post WHERE id = ?', (post_id,)).fetchone()
        
        if post is None:
            abort(404, f"Post id {post_id} doesn't exist.")
            
        db.execute(
            'INSERT INTO comment (body, author_id, post_id) VALUES (?, ?, ?)',
            (body, g.user['id'], post_id)
        )
        db.commit()
        flash('Your comment has been added.', 'success')
    
    return redirect(url_for('blog.view', id=post_id))

@bp.route('/comment/<int:id>/delete', methods=['POST'])
@login_required
def delete_comment(id):
    db = get_db()
    comment = db.execute(
        'SELECT c.id, c.author_id, c.post_id, p.author_id as post_author_id'
        ' FROM comment c JOIN post p ON c.post_id = p.id'
        ' WHERE c.id = ?',
        (id,)
    ).fetchone()

    if comment is None:
        abort(404, f"Comment id {id} doesn't exist.")
    
    # Allow both comment author and post author to delete comments
    if comment['author_id'] != g.user['id'] and comment['post_author_id'] != g.user['id']:
        abort(403)

    db.execute('DELETE FROM comment WHERE id = ?', (id,))
    db.commit()
    flash('Comment deleted.', 'success')
    
    return redirect(url_for('blog.view', id=comment['post_id']))
