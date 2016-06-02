import os

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database we are going to use.
# Using SQLite for testing.
# You may want to switch to another database management system
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
DATABASE_CONNECT_OPTIONS = {}

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
