"""Application initialization."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('settings')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Build the database
db.create_all()

# Initialize the Flask login manager
login_manager = LoginManager()
login_manager.init_app(app)