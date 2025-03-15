from flask import(
    Blueprint, flash, g, redirect, render_template, 
    request, url_for, current_app
)
from flask_login import login_required, current_user
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from Blog.auth import login_required
from Blog.db import get_db
import os
import bleach
<<<<<<< HEAD
=======
from math import ceil
from flask import jsonify
from datetime import datetime  
>>>>>>> 6766143 (jsonify output)

bp = Blueprint('blog', __name__)

POST_IMAGE_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


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

    if check_author and post['author_id'] != current_user.id:
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
    
<<<<<<< HEAD
    return render_template('blog/index.html', posts=posts_with_images)

=======
    return {
        'posts': posts_with_images,
        'total_pages': total_pages,
        'current_page': page,
        'total_posts': total_posts,
        'per_page': per_page
    }


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
        
        # Convert datetime objects to ISO format strings for JSON serialization
        if isinstance(post_dict['created'], datetime):
            post_dict['created'] = post_dict['created'].isoformat()
        
        posts_with_images.append(post_dict)
    
    # Return JSON response
    return jsonify(posts=posts_with_images)
>>>>>>> 6766143 (jsonify output)

@bp.route('/<int:id>/view')
def view(id):
    post = get_post(id, check_author=False)
    comments = get_post_comments(id)
    
    # Convert datetime objects to serializable format for JSON
    post_copy = dict(post)
    if isinstance(post_copy['created'], datetime):
        post_copy['created'] = post_copy['created'].isoformat()
    
    comments_copy = []
    for comment in comments:
        comment_dict = dict(comment)
        if isinstance(comment_dict['created'], datetime):
            comment_dict['created'] = comment_dict['created'].isoformat()
        comments_copy.append(comment_dict)
    
    # Return JSON response
    return jsonify({
        'post': post_copy,
        'comments': comments_copy
    })


@bp.route('/create', methods=['POST'])
@login_required 
def create():
    if not current_user.is_authenticated:
        print(" DEBUG: User is not authenticated!")  
        return jsonify({"status": "error", "message": "Authentication required"}), 401

    try:
        # Check if the request is JSON or form-data
        if request.is_json:
            data = request.get_json()
            title = data.get('title', '').strip()
            body = data.get('body', '').strip()
        else:
            title = request.form.get('title', '').strip()
            body = request.form.get('body', '').strip()
        
        if not title:
            return jsonify({"status": "error", "message": "Title is required"}), 400

        db = get_db()
        
        # Insert post into database
        cursor = db.execute(
            'INSERT INTO post (title, body, author_id, created)'
            ' VALUES (?, ?, ?, ?)',
            (title, body, current_user.id, datetime.utcnow())
        )
        post_id = cursor.lastrowid

        uploaded_images = []
        
        # Handle file uploads (only for form submissions)
        if not request.is_json and 'images' in request.files:
            images = request.files.getlist('images')                
            upload_folder = current_app.config.get('POST_IMAGE_FOLDER', 'static/uploads')
            os.makedirs(upload_folder, exist_ok=True)

            for file in images:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)

                    image_url = f'uploads/{filename}'

                    # Save image path to database
                    db.execute(
                        'INSERT INTO post_images (post_id, image_url) VALUES (?, ?)',
                        (post_id, image_url)
                    )
                    uploaded_images.append(image_url)

        db.commit()

        # Fetch the complete post details including images
        post = db.execute(
            'SELECT p.id, p.title, p.body, p.created, p.author_id, u.username'
            ' FROM post p'
            ' JOIN user u ON p.author_id = u.id'
            ' WHERE p.id = ?',
            (post_id,)
        ).fetchone()

        if not post:
            return jsonify({"status": "error", "message": "Post not found after creation"}), 500

        # Convert to dictionary
        post_dict = dict(post)

        # Convert datetime to string
        if isinstance(post_dict['created'], datetime):
            post_dict['created'] = post_dict['created'].isoformat()

        # Add images to the post dictionary
        post_dict['images'] = uploaded_images

        return jsonify({
            "status": "success",
            "message": "Post created successfully",
            "post": post_dict,
            "redirect": url_for('blog.index')
        }), 201

    except Exception as e:
        db.rollback() if 'db' in locals() else None
        print(f" ERROR: {str(e)}")  #  Debugging
        return jsonify({
            "status": "error",
            "message": "Error creating post",
            "details": str(e)
        }), 500





@bp.route('/update/<int:post_id>', methods=['POST'])
@login_required
def update(post_id):
    if not current_user.is_authenticated:
        return jsonify({"status": "error", "message": "Authentication required"}), 401

    db = get_db()

    try:
        # Fetch the existing post
        post = db.execute(
            'SELECT * FROM post WHERE id = ? AND author_id = ?', (post_id, current_user.id)
        ).fetchone()

        if not post:
            return jsonify({"status": "error", "message": "Post not found or unauthorized"}), 404

        # **Get updated data**
        title = request.form.get('title', post['title']).strip()
        body = request.form.get('body', post['body']).strip()
        images_to_delete = request.form.getlist('images_to_delete')

        #Update Post Title & Body
        db.execute('UPDATE post SET title = ?, body = ? WHERE id = ?', (title, body, post_id))

        
        
        # DELETE Old Images
        if images_to_delete:
            for img in images_to_delete:
                image_filename = os.path.basename(img)  # Extract only the filename
                image_path = os.path.join(current_app.config['POST_IMAGE_FOLDER'], image_filename)

                try:
                    if os.path.isfile(image_path):  
                        os.remove(image_path)  # Delete from filesystem
                        print(f"Deleted image file: {image_filename}")
                    else:
                        print(f"Image file not found: {image_path}")  # Debugging log

                    # Delete from database regardless of file existence
                    cursor = db.execute('DELETE FROM post_images WHERE post_id = ? AND image_url = ?', 
                                        (post_id, f'uploads/{image_filename}'))
                    db.commit()
                    
                    if cursor.rowcount > 0:
                        print(f"Deleted image from database: {image_filename}")
                    else:
                        print(f"No database entry found for: {image_filename}")

                except Exception as e:
                    print(f"Error deleting image {image_filename}: {str(e)}")
                
        # Upload New Images (If Any)
        uploaded_images = []
        if 'images' in request.files:
            images = request.files.getlist('images')
            upload_folder = os.path.join(current_app.static_folder, 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            for file in images:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)

                    image_url = f'uploads/{filename}'
                    db.execute('INSERT INTO post_images (post_id, image_url) VALUES (?, ?)', (post_id, image_url))
                    uploaded_images.append(image_url)

        db.commit()  

        # Fetch Updated Post Details
        updated_post = db.execute(
            'SELECT p.id, p.title, p.body, p.created, u.username FROM post p '
            'JOIN user u ON p.author_id = u.id WHERE p.id = ?', (post_id,)
        ).fetchone()

        # Fetch Updated Images
        updated_images = db.execute(
            'SELECT image_url FROM post_images WHERE post_id = ?', (post_id,)
        ).fetchall()
        updated_images = [img['image_url'] for img in updated_images]

        return jsonify({
            "status": "success",
            "message": "Post updated successfully",
            "post": dict(updated_post) if updated_post else None,
            "images": updated_images
        }), 200

    except Exception as e:
        db.rollback()
        print(f"ERROR: {str(e)}")
        return jsonify({"status": "error", "message": "Error updating post", "details": str(e)}), 500



<<<<<<< HEAD
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
=======
@bp.route('/delete/<int:id>', methods=['DELETE'])
>>>>>>> 6766143 (jsonify output)
@login_required
def delete(id):
    post = get_post(id)
    if not post:
        return jsonify({'success': False, 'error': 'Post not found'}), 404
    
    db = get_db()
    try:
        for image_url in post['images']:
            try:
                image_path = os.path.join(current_app.static_folder, image_url)
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"Error deleting image file: {e}")

        db.execute('DELETE FROM post_images WHERE post_id = ?', (id,))
        db.execute('DELETE FROM post WHERE id = ?', (id,))
        db.commit()

        return jsonify({'success': True, 'message': 'Post was successfully deleted.', 'redirect': url_for('blog.index')})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': 'Error deleting post.', 'details': str(e)}), 500

<<<<<<< HEAD
=======

# Add comment route with JSON support

>>>>>>> 6766143 (jsonify output)
@bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    try:
        # Check if request is JSON or Form Data
        if request.is_json:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON request'}), 400
            body = data.get('body', '').strip()
        else:
            body = request.form.get('body', '').strip()
        
        if not body:
            return jsonify({'error': 'Comment cannot be empty.'}), 400
        
        db = get_db()
        
        # Ensure the post exists
        post = db.execute('SELECT id FROM post WHERE id = ?', (post_id,)).fetchone()
        if post is None:
            return jsonify({'error': f"Post ID {post_id} does not exist."}), 404

        # Insert the comment
        cursor = db.execute(
            'INSERT INTO comment (body, author_id, post_id) VALUES (?, ?, ?)',
            (body, current_user.id, post_id)  # Use `current_user.id` instead of `g.user['id']`
        )
        comment_id = cursor.lastrowid
        db.commit()

        # Fetch the newly created comment
        comment = db.execute(
            '''
            SELECT c.id, c.body, c.created, c.author_id, u.username
            FROM comment c
            JOIN user u ON c.author_id = u.id
            WHERE c.id = ?
            ''',
            (comment_id,)
        ).fetchone()

        if comment is None:
            return jsonify({'error': 'Failed to retrieve the added comment.'}), 500
        
        # Convert result to a dictionary
        comment_dict = dict(comment)
        
        # Convert datetime to string if needed
        if isinstance(comment_dict.get('created'), datetime):
            comment_dict['created'] = comment_dict['created'].isoformat()

        return jsonify({
            'success': True,
            'message': 'Your comment has been added.',
            'comment': comment_dict,
            'redirect': url_for('blog.view', id=post_id)
        })

    except Exception as e:
        db.rollback()  # Ensure rollback in case of failure
        return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500

<<<<<<< HEAD
@bp.route('/comment/<int:id>/delete', methods=['POST'])
=======

# Delete comment route with JSON support
@bp.route('/comment/<int:id>/delete', methods=['DELETE'])
>>>>>>> 6766143 (jsonify output)
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
        return jsonify({'error': f"Comment id {id} doesn't exist."}), 404
    
    # Allow both comment author and post author to delete comments
    if comment['author_id'] != current_user.id and comment['post_author_id'] != current_user.id:
        return jsonify({'error': 'Unauthorized to delete this comment.'}), 403

    post_id = comment['post_id']
    
    db.execute('DELETE FROM comment WHERE id = ?', (id,))
    db.commit()
    
    return jsonify({
        'success': True,
        'message': 'Comment deleted.',
        'redirect': url_for('blog.view', id=post_id)
    })
