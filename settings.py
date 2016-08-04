"""Settings for Botos. This can be different per site."""
import os
import logging

# # App hosting settings
APP_HOST = '0.0.0.0'
APP_PORT = 8080
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
WTF_CSRF_ENABLED = True
SECRET_KEY = 'change-this-before-deploying'

BCRYPT_LOG_ROUNDS = 12

# Log storage
LOG_FILENAME = 'app.log'
LOG_LEVEL = logging.DEBUG  # Change to logging.INFO during production

# Location to store generated XLSX files.
XLSX_DIRECTORY = BASE_DIR + 'botos/botos-content/xlsx'
PDF_DIRECTORY = BASE_DIR + 'botos/botos-content/pdf'

# Location to store the profile pictures.
PROF_DIRECTORY = BASE_DIR + 'botos/botos-content/candidate-img'

# Allowed extensions to be uploaded in the candidate registration form.
ALLOWED_EXTENSIONS = [
    'png',
    'gif',
    'jpg',
    'jpeg'
]

# TODO: Move some of the settings here to the SettingsModel.
