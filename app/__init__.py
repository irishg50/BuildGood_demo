import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from .extensions import db, migrate

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # Use config from Config class (which loads DATABASE_URL from .env or uses the default)
    app.config.from_object(Config)
    
    # Debug: Print database connection details
    db_url = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"\n[DEBUG] Attempting to connect to database:")
    print(f"[DEBUG] Database URL: {db_url}")
    
    if test_config is not None:
        # Load the test config if passed in
        app.config.from_mapping(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Ensure the upload folder exists
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        pass
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from .routes.main import bp as main_bp
    from .routes.research import bp as research_bp
    from .routes.resources import bp as resources_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(research_bp, url_prefix='/research')
    app.register_blueprint(resources_bp, url_prefix='/resources')

    # Create database tables
    with app.app_context():
        try:
            # Create tables if they don't exist
            print("[DEBUG] Creating tables if they don't exist...")
            db.create_all()
            print("[DEBUG] Tables created/verified successfully")
            
            # Verify the resources table structure
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('resources')
            print("[DEBUG] Resources table columns:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
                
        except Exception as e:
            print(f"[DEBUG] Error during database initialization: {str(e)}")
            raise
    
    return app 