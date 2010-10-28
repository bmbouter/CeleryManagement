"""
    Settings for tests which do not require external Celery processes like 
    celeryd and celeryev.
"""

from settings import *
from celeryconfig import *

#==============================================================================#
# This file is included in version control.  Do not add sensitive information  #
# here.                                                                        #
#==============================================================================#

if CELERYMANAGEMENT_USING_HUDSON:
    print "CeleryManagement: Configuring for Hudson tests..."
    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
    INSTALLED_APPS = INSTALLED_APPS + ('django_nose',)
    CELERY_RESULT_BACKEND = "database"
    CELERY_RESULT_DBURI = "sqlite:///celery.db"

# Make sure CELERY_IMPORTS is defined.  Then add test tasks module to it.
CELERY_IMPORTS = globals().get('CELERY_IMPORTS',())
CELERY_IMPORTS = CELERY_IMPORTS + ('celerymanagementapp.testutil.tasks',)

CELERY_ALWAYS_EAGER = True

