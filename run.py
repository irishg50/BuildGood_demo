import os
from dotenv import load_dotenv
from app import create_app
from app.extensions import db
from app.models.resource import Resource

# Load environment variables
load_dotenv()

# Create the application instance
app = create_app()

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

@app.shell_context_processor
def make_shell_context():
    """Add database models to Flask shell context."""
    return {
        'db': db,
        'Resource': Resource
    }

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',  # Make the server publicly available
        port=port,
        debug=os.environ.get('FLASK_ENV') == 'development'  # Enable debug mode in development
    ) 