"""Settings for Botos. This can be different per site."""
import os
import logging

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__)) + '/'

# Define the database we are going to use.
# Using SQLite for testing.
# You may want to switch to another database management system
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'botos_app.db')
DATABASE_CONNECT_OPTIONS = {}

# We do not need to use Flask-SQLAlchemy's event system
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Application threads. A common general assumption is
# using 2 per available processor cores to handle
# incoming requests using one and performing
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection against Cross-site Request Forgery (CRSF)
CSRF_ENABLED = True

# Use a secure, unique, and absolutely secret key for
# signing the data
CSRF_SESSION_KEY = ''

# Secret key for signing cookies
SECRET_KEY = ''

# Log storage
LOG_FILENAME = 'app.log'
LOG_LEVEL = logging.DEBUG  # Change to logging.INFO during production

# TODO: Move some of the settings here to the SettingsModel.