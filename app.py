import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the Base class
db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///mep_system.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Maximum file upload size (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Initialize the database with the app
db.init_app(app)

# Create tables within app context
with app.app_context():
    # Import models to create tables
    import models  # noqa: F401
    db.create_all()
    logger.info("Database tables created")
