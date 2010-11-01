"""
    Run tests which require real celeryd and celeryev processes.
    
    To run tests this way, use:
        django-admin.py testcelery --settings=testcelery_settings ...
        
    The special settings file is required to make sure that both the test and 
    celery processes use the same settings.  It must define both the 'NAME' and 
    'TEST_NAME' database settings.  Normally, django uses different databases 
    when testing than when not testing.  This is a simple hack to overcome this 
    behavior while still deriving from DjangoTestSuiteRunner.
    
    This will load all tests from the suite() function in the 
    celerymanagementapp.tests_celery module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest
    
import subprocess
    
from django.core.management.commands import syncdb
from django.test.simple import DjangoTestSuiteRunner
from django.conf import settings


CMDBASE = 'django-admin.py'
SETTINGS = '--settings=testcelery_settings'
PYPATH = "--pythonpath=."
CAMERA = 'djcelery.snapshot.Camera'
CAMFREQ = '0.1'
CELERYDLOG='celeryd.log.txt'
CELERYEVLOG='celeryev.log.txt'

ARGS_CELERYD = [CMDBASE, 'celeryd', '-E','-B','-f', CELERYDLOG, SETTINGS, PYPATH]
ARGS_CELERYEV = [CMDBASE, 'celeryev', '-c',CAMERA, '--frequency={0}'.format(CAMFREQ),'-f',CELERYEVLOG, SETTINGS, PYPATH]


class TestRunner(DjangoTestSuiteRunner):
    def __init__(self, verbosity=1, interactive=True, failfast=True, tests=[], **kwargs):
        super(TestRunner,self).__init__(verbosity, interactive, failfast, **kwargs)
        self.testlist = tests
    
    def build_suite(self):
        suite = unittest.TestSuite()
        loader = unittest.TestLoader()
        for testcase in self.testlist:
            if isinstance(testcase, unittest.TestCase):
                suite.addTest(loader.loadTestsFromTestCase(testcase))
            elif isinstance(testcase, unittest.TestSuite):
                suite.addTest(testcase)
            else:
                msg = 'Unrecognized type for given testcase.  '
                msg += 'Must be TestSuite or TestCase.\n'
                msg += '  type is: {0}'.format(type(testcase))
                raise RuntimeError(msg)
        return suite
        
    def run_tests(self):
        with DBContextManager(self):
            suite = self.build_suite()
            with CeleryContextManager():
                result = self.run_suite(suite)
        return self.suite_result(suite, result)
        
        
class DBContextManager(object):
    def __init__(self, runner):
        self.runner = runner
        
    def __enter__(self):
        self.runner.setup_test_environment()
        self.oldconfig = self.runner.setup_databases()
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.runner.teardown_databases(self.oldconfig)
        self.runner.teardown_test_environment()
        
        
class CeleryContextManager(object):
    def __init__(self):
        self.celeryd = None
        self.celeryev = None
        
    def terminate(self):
        if self.celeryd and not self.celeryd.poll():
            print 'Terminating celeryd...'
            self.celeryd.terminate()
            self.celeryd.wait()
        if self.celeryev and not self.celeryev.poll():
            print 'Terminating celeryev...'
            self.celeryev.terminate()
            self.celeryev.wait()
        
    def __enter__(self):
        try:
            print 'Launching celeryd...'
            self.celeryd = subprocess.Popen(ARGS_CELERYD)
            print 'Launching celeryev...'
            self.celeryev = subprocess.Popen(ARGS_CELERYEV)
        except Exception:
            print '...Error encountered launching celery processes!'
            self.terminate()
            raise
        print '...celeryd and celeryev launched successfully!'
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()
        
        
def runtests(tests, verbosity=1):
    runner = TestRunner(verbosity=verbosity, tests=tests)
    runner.run_tests()


def get_test_cases():
    from celerymanagementapp import tests_celery
    suite = tests_celery.suite()
    return [suite]


def main():
    defaultdb = settings.DATABASES['default']
    if not defaultdb.get('TEST_NAME',None):
        raise RuntimeError('The setting DATABASES.TEST_NAME must be defined.')
    if defaultdb['TEST_NAME'] != defaultdb['NAME']:
        raise RuntimeError('The settings DATABASES.TEST_NAME and DATABASE.NAME must be identical.')
    
    testcases = get_test_cases()
    runtests(tests=testcases)


if __name__=='__main__':
    main()


