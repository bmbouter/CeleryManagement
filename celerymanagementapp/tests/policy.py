import datetime
import traceback
import types

from celerymanagementapp.tests import base
from celerymanagementapp import policy
from celerymanagementapp.policy import exceptions
from celerymanagementapp.policy.policy import _apply_runner
from celerymanagementapp.policy.env import ModuleWrapper



#==============================================================================#
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
        
#==============================================================================#
class Env_TestCase(base.CeleryManagement_TestCaseBase):
    def check_object_dict(self, name, obj):
        if isinstance(obj, ModuleWrapper):
            dict = obj.__dict__['data']
        else:
            dict = obj.__dict__
        for k,v in dict.iteritems():
            try:
                # none of an object's attributes should be a module
                self.assertFalse(isinstance(v, types.ModuleType))
            except Exception as e:
                msg = '\n    Note: obj was: {0}.{1}'.format(name,k)
                e.args = e.args[0:1] + (msg,) + e.args[1:]
                raise
        
    def test_modules(self):
        self.assertFalse(isinstance(_apply_runner.globals['time'], types.ModuleType))
        self.assertEquals(type(_apply_runner.globals['datetime']), ModuleWrapper)
        self.assertEquals(type(_apply_runner.globals['calendar']), ModuleWrapper)
        self.assertEquals(type(_apply_runner.globals['time']), ModuleWrapper)
        self.assertEquals(type(_apply_runner.globals['math']), ModuleWrapper)
        
                
    def test_names(self):
        globals = _apply_runner.globals
        for k,v in _apply_runner.globals.iteritems():
            if hasattr(v, '__dict__'):
                self.check_object_dict(k,v)
                


#==============================================================================#
class Section_TestCaseBase(base.CeleryManagement_TestCaseBase):
    _tmpl = None  # must be a string containing {src}
    def src(self, src):
        """ Indents source code.  Embedded newlines are allowed. """
        indent = ' '*4*2
        src = '\n'.join('{0}{1}'.format(indent,s) for s in src.splitlines())
        return self._tmpl.format(src=src)
    
    
#==============================================================================#
class ScheduleSection_TestCase(Section_TestCaseBase):
    pass
    
    
class ConditionSection_TestCase(Section_TestCaseBase):
    _tmpl = '''\
policy:
    schedule:
        1
    condition:
{src}
    apply:
        10

    '''
        
    def test_allowed(self):
        exprs = [ 'True','False','None', 
                  'a==b', 'a and (b or c)',
                  '[a for b in c]',
                  '[a for b in c if d]',
                  '(a for b in c if d)',
                  'a if b else c',
                  'func(keyword=value)',
                ]
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
                
    def test_null_condition(self):
        _testdata = '''
policy:
    schedule:
        1
    apply:
        1
'''
        # Should not cause an exception...
        p = policy.Policy(_testdata)

        
class ApplySection_TestCase(Section_TestCaseBase):
    _tmpl = '''\
policy:
    schedule:
        1
    condition:
        True
    apply:
{src}

    '''
        
    def test_allowed(self):
        exprs = [ 'True','False','None', 
                  'a = b', 'a and (b or c)',
                  'if True: pass',
                  'x = [a for b in c]',
                  'x = [a for b in c if d]',
                  'x = (a for b in c if d)',
                  'a if b else c',
                ]
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
                  'for x in y: pass',
                  'yield z',
                ]
        for expr in exprs:
            testdata = self.src(expr)
            try:
                self.assertRaises(exceptions.SyntaxError, policy.Policy, testdata)
            except Exception as e:
                msg = '\n    Note: expr was: {0}'.format(expr)
                e.args = (e.args[0] + msg,) + e.args[1:]
                raise
        
    def test_unassignable_error(self):
        exprs = [ 'workers = 5',
                  'datetime = 1',
                ]
        for expr in exprs:
            testdata = self.src(expr)
            try:
                self.assertRaises(exceptions.SyntaxError, policy.Policy, testdata)
            except Exception as e:
                msg = '\n    Note: expr was: {0}'.format(expr)
                e.args = (e.args[0] + msg,) + e.args[1:]
                raise


#==============================================================================#
class ApplySectionExec_TestCase(Section_TestCaseBase):
    _tmpl = '''\
policy:
    schedule:
        1
    condition:
        True
    apply:
{src}

    '''
    
    def test_basic(self):
        expr = 'x = 5'
        testdata = self.src(expr)
        p = policy.Policy(testdata)
        r = p.run_apply()
        self.assertEquals(5, _apply_runner.last_locals['x'])
    
    def test_basic_api(self):
        testdata = self.src('t = time.time()')
        p = policy.Policy(testdata)
        r = p.run_apply()
        self.assertEquals(float, type(_apply_runner.last_locals['t']))
        
#==============================================================================#




