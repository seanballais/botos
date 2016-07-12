"""Application initialization."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from botos.modules.app_settings.settings import Settings

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

# Generate the settings table records.
if not Settings.property_exists('current_template'):
    Settings.add_property('current_template')
    Settings.set_property('current_template',
                          'default'
                          )