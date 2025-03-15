import sqlite3
import os
from datetime import datetime 
import click
from flask import current_app, g 


def get_db():
    """Ensure `get_db()` runs inside Flask app context."""
    if not current_app:
        raise RuntimeError("`get_db()` called outside of Flask app context")

    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES    
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception as e:
            current_app.logger.error(f"Error closing database: {e}")



def init_db():
    """Initialize the database with schema."""
    with current_app.app_context():        
        db = get_db()
        try:
            with current_app.open_resource('schema.sql') as f:
                script = f.read().decode('utf8')
                with db:  # Use transaction block
                    for statement in script.split(';'):
                        if statement.strip():
                            db.execute(statement)
        except sqlite3.OperationalError as e:
            current_app.logger.error(f"Database error: {e}")
            raise



@click.command('init-db')
@click.option('--force', is_flag=True, help='Force recreate all tables')
def init_db_command(force):
    """Clear the existing data and create new tables."""
    with current_app.app_context():  
        if force:
            # Drop all tables if force flag is used
            db = get_db()
            db.executescript('''
                DROP TABLE IF EXISTS post_images;
                DROP TABLE IF EXISTS post;
                DROP TABLE IF EXISTS user;
            ''')
            db.commit()

        init_db()
        click.echo('Initialized the database.')


sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)


def init_app(app):
    """Initialize database with Flask app."""
    os.makedirs(app.instance_path, exist_ok=True)  

    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

