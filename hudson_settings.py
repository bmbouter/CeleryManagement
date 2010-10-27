from test_settings import *

# This is included in version control.  Do not add sensitive information here.

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

INSTALLED_APPS = INSTALLED_APPS + ('django_nose',)
