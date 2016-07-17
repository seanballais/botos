"""Application initialization."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('settings')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Set up a Bcrypt instance
bcrypt = Bcrypt(app)

# Import the modules before creating the tables
from botos.modules.app_data import models

# Build the database
db.create_all()

from botos.modules.app_data.controllers import Settings
# Generate the settings table records.
if not Settings.property_exists('current_template'):
    Settings.add_property('current_template')
    Settings.set_property('current_template',
                          'default'
                          )

if not Settings.property_exists('title'):
    Settings.add_property('title')
    Settings.set_property('title',
                          'Election System'
                          )

# Initialize the Flask login manager
login_manager = LoginManager()
login_manager.init_app(app)