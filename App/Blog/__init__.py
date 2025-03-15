import os
from flask import Flask
from flask_session import Session
from flask_login import LoginManager
from Blog.db import get_db

#  Initialize LoginManager before importing auth
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

  
    app.config.from_mapping(
        SECRET_KEY='dev',
        SESSION_TYPE='filesystem',
        DATABASE=os.path.join(app.instance_path, 'Blog.sqlite'),
        PROFILE_IMAGE_FOLDER=os.path.join(app.root_path, 'static', 'profile_images'),
        POST_IMAGE_FOLDER=os.path.join(app.root_path, 'static', 'uploads'),  # Separate folder for post images
        SESSION_PERMANENT=True,
        SESSION_USE_SIGNER=True,
        SESSION_FILE_DIR=os.path.join(app.instance_path, 'flask_session'),
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_HTTPONLY=True,
    )


    #  Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Ensure the upload directory exists
    os.makedirs(app.config['POST_IMAGE_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROFILE_IMAGE_FOLDER'], exist_ok=True)

    Session(app) 
    login_manager.init_app(app)  
    from Blog.auth import User 

   
    @login_manager.user_loader
    def load_user(user_id):
        print(f"🔍 DEBUG: Loading user {user_id}")  #  Debugging
        return User.get(user_id)  #  Ensure this returns a valid User object
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app

