import os
import sys

# Add project directory to sys.path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = os.path.join(project_dir, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

# Import Flask app as 'application' for WSGI
from app import app as application
