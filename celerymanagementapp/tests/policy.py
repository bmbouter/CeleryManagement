import datetime
import traceback
import types

from celerymanagementapp.tests import base
from celerymanagementapp import policy
from celerymanagementapp.policy import exceptions
from celerymanagementapp.policy.policy import Runner
from celerymanagementapp.policy import env



#==============================================================================#
class Imports_TestCase(base.CeleryManagement_TestCaseBase):
    def test_basic(self):
        import celerymanagementlib.celery_imports
        
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
        
    def test_empty_input(self):
        _testdata = ''
        try:
            p = policy.Policy(_testdata)
        except exceptions.SyntaxError as e:
            self.assertEquals('expected "policy", found ""', e._msg)
        else:
            self.fail('Expected a syntax error.')
        
    def test_missing_policy_header1(self):
        # name
        _testdata = 'zombie'
        try:
            p = policy.Policy(_testdata)
        except exceptions.SyntaxError as e:
            self.assertEquals('expected "policy", found "zombie"', e._msg)
        else:
            self.fail('Expected a syntax error.')
        
    def test_missing_policy_header2(self):
        # digit
        _testdata = '5'
        try:
            p = policy.Policy(_testdata)
        except exceptions.SyntaxError as e:
            self.assertEquals('expected "policy", found "5"', e._msg)
        else:
            self.fail('Expected a syntax error.')
        
    def test_missing_policy_header3(self):
        # indent only
        _testdata = '    '
        try:
            p = policy.Policy(_testdata)
        except exceptions.SyntaxError as e:
            self.assertEquals('expected "policy", found ""', e._msg)
        else:
            self.fail('Expected a syntax error.')
        
    def test_missing_policy_header4(self):
        # indented 'policy'
        _testdata = ' policy:'
        try:
            p = policy.Policy(_testdata)
        except exceptions.SyntaxError as e:
            self.assertEquals('expected "policy", found " "', e._msg)
        else:
            self.fail('Expected a syntax error.')
        
    def test_missing_schedule_header1(self):
        # no 'schedule'
        _testdata = '''\
policy:

'''
        try:
            p = policy.Policy(_testdata)
        except exceptions.SyntaxError as e:
            self.assertEquals('expected "INDENT", found "ENDMARKER"', e._msg)
        else:
            self.fail('Expected a syntax error.')
        
    def test_missing_schedule_header2(self):
        # 'apply' in place of 'schedule'
        _testdata = '''\
policy:
    apply:
'''
        try:
            p = policy.Policy(_testdata)
        except exceptions.SyntaxError as e:
            self.assertEquals('expected "schedule", found "apply"', e._msg)
        else:
            self.fail('Expected a syntax error.')
        
#==============================================================================#
class Env_TestCase(base.CeleryManagement_TestCaseBase):
    def check_object_dict(self, name, obj):
        if isinstance(obj, env.ModuleWrapper):
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
        with Runner(env.ApplyEnv) as runner:
            self.assertFalse(isinstance(runner.globals['time'], types.ModuleType))
            self.assertEquals(type(runner.globals['datetime']), env.ModuleWrapper)
            self.assertEquals(type(runner.globals['calendar']), env.ModuleWrapper)
            self.assertEquals(type(runner.globals['time']), env.ModuleWrapper)
            self.assertEquals(type(runner.globals['math']), env.ModuleWrapper)
        
                
    def test_names(self):
        with Runner(env.ApplyEnv) as runner:
            for k,v in runner.globals.iteritems():
                if hasattr(v, '__dict__'):
                    self.check_object_dict(k,v)
                    
    def test_celery_states(self):
        states = ['PENDING','RECEIVED','STARTED','SUCCESS','FAILURE','REVOKED','RETRY']
        with Runner(env.ApplyEnv) as runner:
            for state in states:
                self.assertEquals(state, runner.globals[state])
                


#==============================================================================#
class Section_TestCaseBase(base.CeleryManagement_TestCaseBase):
    _tmpl = None  # Must be a string containing {src}.
                  # {src} will be indented by 8 chars.
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
                  'func(tasks=value)',  # 'tasks' is normally unassignable
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
                  '_underscore',
                  'class MyClass(object): pass',
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
    
    def test_multi_condition(self):
        _testdata = '''
policy:
    schedule:
        1
    condition:
        True
    condition:
        True
    condition:
        True
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
                  'if True:\n    pass\nelif True:\n    pass\nelse:\n    pass',
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
                  '_underscore',
                  'class MyClass(object): pass',
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
        with Runner(env.ApplyEnv) as runner:
            r = runner(p.apply_code, p.sourcelines) # Policy.run_apply()
        self.assertEquals(5, runner.locals['x'])
    
    def test_basic_api(self):
        testdata = self.src('t = time.time()')
        p = policy.Policy(testdata)
        with Runner(env.ApplyEnv) as runner:
            r = runner(p.apply_code, p.sourcelines) # Policy.run_apply()
        self.assertEquals(float, type(runner.locals['t']))
        
#==============================================================================#
class StatsApi_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_policy_statsapi']
    
    def test_alltasks(self):
        stats = env.ConditionEnv().globals['stats']
        self.assertEquals(9, stats.tasks())
    
    def test_tasks_workers(self):
        stats = env.ConditionEnv().globals['stats']
        self.assertEquals(5, stats.tasks(workers='worker1'))
        self.assertEquals(5, stats.tasks(workers=['worker1']))
        self.assertEquals(9, stats.tasks(workers=['worker1','worker2']))
        self.assertEquals(4, stats.tasks(workers='worker2'))

#==============================================================================#




