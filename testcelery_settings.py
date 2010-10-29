from settings import *
from celeryconfig import *

#==============================================================================#
# This file is included in version control.  Do not add sensitive information  #
# here.                                                                        #
#==============================================================================#

if CELERYMANAGEMENT_USING_HUDSON:
    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
    INSTALLED_APPS = INSTALLED_APPS + ('django_nose',)

# Make sure CELERY_IMPORTS is defined.  Then add test tasks module to it.
CELERY_IMPORTS = globals().get('CELERY_IMPORTS',())
CELERY_IMPORTS = CELERY_IMPORTS + ('celerymanagementapp.testutil.tasks',)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'celerymanagement_test.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
