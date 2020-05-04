"""
This settings file is intended to be used with Travis CI. Feel free to use
this as another template for your own local settings file.
"""
import os

# Keep this a secret! In production, please change this to something else.
SECRET_KEY = 'T6xtu*&k8@)pibt(^c2ox%@#3taw0zp_g05e28g!#0j3gjrf2!RAVIS'

# This should be True when in development. Only disable this in
# staging/production.
DEBUG = True

# For working with databases in Django, please refer to this:
#     https://docs.djangoproject.com/en/2.2/ref/settings/#databases
#
# Note that there is no need to change this section except in production.
# We recommend using PostgreSQL with Botos since that's the database Botos
# deployments have been using. But, feel free to use whatever database suits
# your case.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['BOTOS_CI_DATABASE_NAME'],
        'USER': os.environ['BOTOS_CI_DATABASE_USERNAME'],
        'PASSWORD': '',
        'TEST': {
            'NAME': os.environ['BOTOS_CI_TEST_DATABASE_NAME']
        }
    }
}

DATABASE_URL = os.environ['BOTOS_CI_DATABASE_URL']

# In production, uncomment and set STATIC_ROOT to the template directory.
# STATIC_ROOT = '/path/to/template/directory'

# In production, uncomment and set STATIC_ROOT to the media directory.
# MEDIA_ROOT = '/path/to/media/directory'
