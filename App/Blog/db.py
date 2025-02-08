import sqlite3
from datetime import datetime 
import click
from flask import current_app, g 

def get_db():
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
        db.close()

def init_db():
    """Initialize the database with schema."""
    db = get_db()
    
    try:
        with current_app.open_resource('schema.sql') as f:
            # Execute schema in a transaction
            script = f.read().decode('utf8')
            # Split the script into individual statements
            statements = script.split(';')
            for statement in statements:
                if statement.strip():  # Skip empty statements
                    try:
                        db.execute(statement)
                    except sqlite3.OperationalError as e:
                        # Log the error but continue with other statements
                        current_app.logger.warning(f"Error executing statement: {e}")
            db.commit()
    except Exception as e:
        db.rollback()  # Rollback in case of errors
        current_app.logger.error(f"Database initialization failed: {e}")
        raise

@click.command('init-db')
@click.option('--force', is_flag=True, help='Force recreate all tables')
def init_db_command(force):
    """Clear the existing data and create new tables."""
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
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
