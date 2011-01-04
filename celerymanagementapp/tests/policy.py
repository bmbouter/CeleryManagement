
from celerymanagementapp.tests import base
from celerymanagementapp import policy

class Policy_TestCase(base.CeleryManagement_TestCaseBase):
    def test_basic(self):
        _testdata = '''\
policy:
    schedule:
        5
    condition:
        1 == 2
    condition:
        3 <= 4
    apply:
        10

'''
        p = policy.Policy(_testdata)
        self.assertEquals(True, p.run_condition())
        self.assertEquals(None, p.run_apply())



