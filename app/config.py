import os
from dotenv import load_dotenv

# Get the absolute path to the project root directory
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
env_path = os.path.join(basedir, '.env')

# Debug: Print the actual contents of .env file
print("\n[DEBUG] Attempting to read .env file directly:")
try:
    with open(env_path, 'r') as f:
        print("[DEBUG] .env file contents:")
        for line in f:
            if 'DATABASE_URL' in line:
                print(f"[DEBUG] Found DATABASE_URL line: {line.strip()}")
except Exception as e:
    print(f"[DEBUG] Error reading .env file: {str(e)}")

# Try loading with dotenv
load_dotenv(env_path)

# Debug: Print environment variables
print("\n[DEBUG] Environment variables after loading:")
print(f"[DEBUG] DATABASE_URL in environment: {os.environ.get('DATABASE_URL')}")

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # Try to get DATABASE_URL from environment, with fallback to direct file reading
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('DATABASE_URL='):
                        SQLALCHEMY_DATABASE_URI = line.strip().split('=', 1)[1]
                        break
        except Exception as e:
            print(f"[DEBUG] Error reading DATABASE_URL from file: {str(e)}")
    
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is not set")
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Research agent settings
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    MAX_RESEARCH_RESULTS = 10
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    
    # Cache settings
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300 