import datetime
import traceback

from celerymanagementapp.tests import base
from celerymanagementapp import policy
from celerymanagementapp.policy import exceptions


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
        
class ScheduleSection_TestCase(base.CeleryManagement_TestCaseBase):
    pass
        
class ConditionSection_TestCase(base.CeleryManagement_TestCaseBase):
    _tmpl = '''\
policy:
    schedule:
        1
    condition:
{src}
    apply:
        10

    '''
    def src(self, src):
        indent = ' '*4*2
        src = '\n'.join('{0}{1}'.format(indent,s) for s in src.splitlines())
        return self._tmpl.format(src=src)
        
    def test_allowed(self):
        exprs = [ 'True','False','None', 'a==b', 'a and (b or c)',]
        for expr in exprs:
            testdata = self.src(expr)
            try:
                p = policy.Policy(testdata)
            except exceptions.Error:
                exc = traceback.format_exc()
                msg = 'condition compilation failed for expr: {0}\n'.format(expr)
                msg += 'original exception: \n{0}\n'.format(exc)
                self.fail(msg)
        
    def test_syntax_error(self):
        exprs = [ 'if True: pass',
                  'while true: pass',
                  'import sys',
                  'def func(): pass',
                  'a = b', 
                ]
        for expr in exprs:
            testdata = self.src(expr)
            try:
                self.assertRaises(exceptions.SyntaxError, policy.Policy, testdata)
            except Exception as e:
                # Append the expr name to the exception info.
                msg = '\n    Note: expr was: {0}'.format(expr)
                e.args = (e.args[0] + msg,) + e.args[1:]
                raise

        
class ApplySection_TestCase(base.CeleryManagement_TestCaseBase):
    _tmpl = '''\
policy:
    schedule:
        1
    condition:
        True
    apply:
{src}

    '''
    def src(self, src):
        indent = ' '*4*2
        src = '\n'.join('{0}{1}'.format(indent,s) for s in src.splitlines())
        return self._tmpl.format(src=src)
        
    def test_allowed(self):
        exprs = [ 'True','False','None', 'a = b', 'a and (b or c)','if True: pass',]
        for expr in exprs:
            testdata = self.src(expr)
            try:
                p = policy.Policy(testdata)
            except exceptions.Error:
                exc = traceback.format_exc()
                msg = 'apply compilation failed for expr: {0}\n'.format(expr)
                msg += 'original exception: \n{0}\n'.format(exc)
                self.fail(msg)
        
    def test_syntax_error(self):
        exprs = [ 'while true: pass',
                  'import sys',
                  'def func(): pass',
                ]
        for expr in exprs:
            testdata = self.src(expr)
            try:
                self.assertRaises(exceptions.SyntaxError, policy.Policy, testdata)
            except Exception as e:
                msg = '\n    Note: expr was: {0}'.format(expr)
                e.args = (e.args[0] + msg,) + e.args[1:]
                raise

