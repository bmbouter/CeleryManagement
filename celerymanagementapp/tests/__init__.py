import unittest

from celerymanagementapp.tests import base

#==============================================================================#
# Test modules...
from celerymanagementapp.tests import stats, segmentize, jsonquery, dataviews, views
from celerymanagementapp.tests import jsonutil

# List of all test modules containing tests.  
_testmodules = [stats, segmentize, jsonquery, dataviews, jsonutil, views]

# Import all test cases so they appear in this module.  This appears to be 
# needed for Hudson automated testing.  Do this instead of just: 
#       from <module> import *
# so we don't import *all* names from the modules.
for m in _testmodules:
    for name,val in m.__dict__.iteritems():
        if name.endswith('_TestCase') and issubclass(val, base.CeleryManagement_TestCaseBase):
            globals()[name] = val

#==============================================================================#

def suite():
    test_suite = unittest.TestSuite()
    for m in _testmodules:
        s = base.autogenerate_testsuite(m.__dict__)
        test_suite.addTest(s)
    return test_suite

#==============================================================================#
