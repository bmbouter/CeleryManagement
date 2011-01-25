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
from celerymanagementapp.testutil.unittest import unittest
    
import subprocess
import os
import signal
    
from django.core.management.commands import syncdb
from django.test.simple import DjangoTestSuiteRunner
from django.conf import settings

from celerymanagementapp.testutil import process

#CAMFREQ = '0.1'
#CELERYDLOG='celeryd.log.txt'
#CELERYEVLOG='celeryev.log.txt'

#ARGS_CELERYD = [CMDBASE, 'celeryd', '-E','-B','-f', CELERYDLOG, SETTINGS, PYPATH]
#ARGS_CELERYEV = [CMDBASE, 'celeryev', '-c',CAMERA, '--frequency={0}'.format(CAMFREQ),'-f',CELERYEVLOG, SETTINGS, PYPATH]

#DEFAULT_SETTINGS = 'testcelery_settings'
#DEFAULT_PYPATH = '.'
#DEFAULT_CMDBASE = 'django-admin.py'
##PYTHON_PATH = '/home/dpwhite2/CeleryManagementEnv/python_libs'

ENV = os.environ
##oldpypath = ENV.get('PYTHONPATH','')
##if oldpypath:
##    oldpypath += ':'
    
##ENV['PYTHONPATH'] = oldpypath + '/home/dpwhite2/CeleryManagementEnv/python_libs'


class TestRunner(DjangoTestSuiteRunner):
    def __init__(self, verbosity=1, interactive=True, failfast=True, tests=None, options={}, **kwargs):
        super(TestRunner,self).__init__(verbosity, interactive, failfast, **kwargs)
        self.testlist = tests or []
        self.options = options
    
    def build_suite(self, test_labels=None):
        test_labels = test_labels or []
        suite = unittest.TestSuite()
        loader = unittest.TestLoader()
        for testcase in self.testlist:
            if isinstance(testcase, unittest.TestCase):
                if not test_labels or testcase.__class__.__name__ in test_labels:
                    suite.addTest(loader.loadTestsFromTestCase(testcase))
            elif isinstance(testcase, unittest.TestSuite):
                if not test_labels or testcase.__class__.__name__ in test_labels:
                    suite.addTest(testcase)
            else:
                msg = 'Unrecognized type for given testcase.  '
                msg += 'Must be TestSuite or TestCase.\n'
                msg += '  type is: {0}'.format(type(testcase))
                raise RuntimeError(msg)
        return suite
        
    def run_tests(self, test_labels=None):
        options = {
            'settings': self.options.get('settings',None),
            }
        self.setup_test_environment()
        oldconfig = self.setup_databases()
        
        ##with DBContextManager(self):
        suite = self.build_suite(test_labels)
        ##with CeleryContextManager(**options):
        result = self.run_suite(suite)
        
        self.teardown_databases(oldconfig)
        self.teardown_test_environment()
        
        return self.suite_result(suite, result)
        
        
# class DBContextManager(object):
    # def __init__(self, runner):
        # self.runner = runner
        
    # def __enter__(self):
        # self.runner.setup_test_environment()
        # self.oldconfig = self.runner.setup_databases()
        
    # def __exit__(self, exc_type, exc_val, exc_tb):
        # self.runner.teardown_databases(self.oldconfig)
        # self.runner.teardown_test_environment()
        
        
# class CeleryContextManager(object):
    # def __init__(self, settings=None, pythonpath=None, cmdbase=None):
        # self.celeryd = None
        # self.celeryev = None
        # self.settings = settings or DEFAULT_SETTINGS
        # self.pythonpath = pythonpath or DEFAULT_PYPATH
        # self.cmdbase = cmdbase or DEFAULT_CMDBASE
        
    # def _launch_celeryd(self):
        # args = [self.cmdbase, 'celeryd', '-E','-B',
                # '-f', CELERYDLOG, 
                # '--settings={0}'.format(self.settings),
                # '--pythonpath={0}'.format(self.pythonpath),
               # ]
        # return subprocess.Popen(args, env=ENV)
        
    # def _launch_celeryev(self):
        # args = [self.cmdbase, 'cmrun',
                # '-f', CELERYEVLOG,
                # '--frequency={0}'.format(CAMFREQ),
                # '--settings={0}'.format(self.settings),
                # '--pythonpath={0}'.format(self.pythonpath),
               # ]
        # return subprocess.Popen(args, env=ENV)
        
    # def terminate(self):
        # if self.celeryd and not self.celeryd.poll():
            # print 'Terminating celeryd...'
            # self.celeryd.terminate()
            # self.celeryd.wait()
        # if self.celeryev and not self.celeryev.poll():
            # print 'Terminating celeryev...'
            # self.celeryev.send_signal(signal.SIGINT)
            # self.celeryev.wait()
        
    # def __enter__(self):
        # try:
            # print 'Launching celeryd...'
            # self.celeryd = self._launch_celeryd()
            # print 'Launching celeryev...'
            # self.celeryev = self._launch_celeryev()
        # except Exception:
            # print '...Error encountered launching celery processes!'
            # self.terminate()
            # raise
        # print '...celeryd and celeryev launched successfully!'
        
    # def __exit__(self, exc_type, exc_val, exc_tb):
        # self.terminate()
        
        
def runtests(tests, verbosity=1, failfast=False, test_labels=None):
    runner = TestRunner(verbosity=verbosity, tests=tests, failfast=failfast)
    runner.run_tests(test_labels=test_labels)


def get_test_cases():
    from celerymanagementapp import tests_celery
    suite = tests_celery.suite()
    return [suite]


def main(*args, **options):
    # use default django syncdb handler, instead of, say, South's
    from django.core import management
    management._commands['syncdb'] = 'django.core'
    
    defaultdb = settings.DATABASES['default']
    if not defaultdb.get('TEST_NAME',None):
        raise RuntimeError('The setting DATABASES.TEST_NAME must be defined.')
    if defaultdb['TEST_NAME'] != defaultdb['NAME']:
        raise RuntimeError('The settings DATABASES.TEST_NAME and DATABASE.NAME must be identical.')
    
    process.DEFAULT_SETTINGS = settings.SETTINGS_MODULE
    
    testcases = get_test_cases()
    runtests(tests=testcases,test_labels=args)


if __name__=='__main__':
    main()


