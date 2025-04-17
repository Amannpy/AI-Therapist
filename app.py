from flask import Flask
from extensions import db, login_manager
import logging  # Add this import
from dotenv import load_dotenv  # Add this
import os  # Add this

# Load environment variables
load_dotenv()  # Add this

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Configure your app here
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mental_well.db'
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['GOOGLE_GEMINI_API_KEY'] = os.getenv('GOOGLE_GEMINI_API_KEY')  # Add this line
# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create tables within app context
with app.app_context():
    from models import User, Assessment, ChatMessage, EmotionRecord
    db.create_all()

# Import routes
from routes import *

logger.info("Application initialized successfully")
