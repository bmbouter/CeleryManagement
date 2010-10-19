from test_settings import *

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

INSTALLED_APPS = INSTALLED_APPS + ('django_nose',)
