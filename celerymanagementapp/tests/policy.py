import datetime

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


    def test_crontab_basic(self):
        _testdata = '''\
policy:
    schedule:
        crontab(minute="*/5")
    condition:
        1 == 2
    condition:
        3 <= 4
    apply:
        10

'''     
        lastrun = datetime.datetime(2011,1,1,hour=12,minute=0,second=0)
        nowtime = datetime.datetime(2011,1,1,hour=12,minute=1,second=0)
        p = policy.Policy(_testdata)
        # the following is a hack, but I need to explicitly set what 'now' is
        p.schedule.nowfun = lambda: nowtime
        self.assertEquals(True, p.run_condition())
        self.assertEquals(None, p.run_apply())
        self.assertEquals((False,240), p.is_due(lastrun))


