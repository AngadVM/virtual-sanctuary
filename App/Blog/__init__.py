import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()
def create_app(test_config=None):
    # create and configure the app
    
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SECRET_KEY= 'dev',
            DATABASE= os.path.join(app.instance_path, 'Blog.sqlite'),
            # Configuration for file uploads
            MAX_CONTENT_LENGTH = 16 * 1024 * 1024,  # 16MB max file size
            UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads'),
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello world
    @app.route('/tvsblog')
    def tvsblog():
        return 'TVS Blog'

    from . import db 
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')


   
    return app
