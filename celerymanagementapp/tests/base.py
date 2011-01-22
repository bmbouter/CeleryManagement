import re
import unittest
import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from djcelery.models import WorkerState
from celerymanagementapp.models import DispatchedTask, PolicyModel

# Disable Nose test autodiscovery for this module.
__test__ = False

#==============================================================================#
# Test cases are automatically added to the test suite if they derive from 
# CeleryManagement_TestCaseBase and their name ends with _TestCase.

#==============================================================================#
class UserLogin_Context(object):
    """Class for use with Python's with statement to ease the writing of tests 
       that involve user logins.
    """
    def __init__(self, client, username, password):
        self.client = client
        self.username = username
        self.password = password
    def __enter__(self):
        self.client.login(username=self.username, password=self.password)
    def __exit__(self, type, value, traceback):
        self.client.logout()

#==============================================================================#
_re_whitespace = re.compile(r'\s+')
_HTMLTAG = r'''</?[A-Za-z0-9 ='"\\:.%+]+>'''  # includes the tag and attributes
_re_adjacenttags = re.compile(r'('+_HTMLTAG+r')\s+(?='+_HTMLTAG+r')')

class CeleryManagement_TestCaseBase(TestCase):
    """Base TestCase class for all CeleryManagement test cases.  All test cases 
       should be derived from this (directly or indirectly) so they are picked 
       up by the test loader in __init__.py.
    """
    pass
    
class CeleryManagement_DBTestCaseBase(CeleryManagement_TestCaseBase):
    """Base TestCase class for all CeleryManagement test cases which access the 
       database.  This automatically destroys all Model objects in tearDown() 
       among other things.  And for tests that do not require the database, not 
       using this class will speed up execution.
    """
    
    def scoped_login(self, username, password):
        """Allows the login functionality to be used via the with statement, to 
           make coding somewhat simpler.
           
           Example:
                def test_method(self):
                    ...
                    with self.scoped_login('username','password'):
                        # now use self.client object:
                        self.client.get("some_url")
                        ...
                        # The client will be automatically logged out when the 
                        # method exits (even in the case of exceptions).
        """
        return UserLogin_Context(self.client, username, password)
        
    def setUp(self):
        self.today = datetime.date.today()
        #self.client = Client()
        self.users = []
        
    def create_users(self, n):
        """Create n users for a test case.  The users will be named userN where 
           N is the index of the user.  Users can be accessed through the 
           member variable 'users' which is a list of Users.
           
           This method will delete all existing test users before creating new 
           ones.
        """
        for user in self.users:
            user.delete()
        self.users = [
                User.objects.create_user(username="user%d"%i,
                                         email="user%d@example.com"%i,
                                         password="password") 
                for i in range(n)
            ]
    def tearDown(self):
        # For all models used by this app, be sure to delete them here.
        # Example:
        #   MyModel.objects.all().delete()
        #
        WorkerState.objects.all().delete()
        DispatchedTask.objects.all().delete()
        PolicyModel.objects.all().delete()
        
        # delete all test users
        for user in self.users:
            user.delete()
        
        
#==============================================================================#
# Use the following function to generate a TestSuite for a given module.  
# Modules do not have to do this themselves--the package handles this.
def autogenerate_testsuite(globals):
    """globals is a dict of global names.  Test modules should use globals() 
       for this argument.
    """
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for name, val in globals.iteritems():
        if name.endswith('_TestCase') and \
           issubclass(val, CeleryManagement_TestCaseBase):
            test_suite.addTest(loader.loadTestsFromTestCase(val))
    return test_suite
    
