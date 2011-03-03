import datetime
import traceback
import types

from celerymanagementapp.tests import base
from celerymanagementapp import policy
from celerymanagementapp.policy import exceptions, env, api
from celerymanagementapp.policy.policy import Runner



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
                
    def test_syntax_error(self):
        # genuine Python syntax errors.
        exprs = [ 'if False then\nx=1',
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
        
    def test_send_mail(self):
        from django.core import mail as django_mail
        
        subj = 'Test Email'
        msg = 'This is a test email.'
        frm = 'from@example.org'
        to = '["to@example.org"]'
        testdata = self.src('send_email("{subj}","{msg}","{frm}",{to})'.format(
                                subj=subj, msg=msg, frm=frm, to=to)
                            )
        p = policy.Policy(testdata)
        with Runner(env.ApplyEnv) as runner:
            r = runner(p.apply_code, p.sourcelines) # Policy.run_apply()
        self.assertEquals(1, len(django_mail.outbox))
        self.assertEquals('Test Email', django_mail.outbox[0].subject)
        self.assertEquals('from@example.org', django_mail.outbox[0].from_email)
        self.assertEquals(['to@example.org'], django_mail.outbox[0].recipients())
        
    def test_name_error(self):
        testdata = self.src('a = unknown_function()')
        p = policy.Policy(testdata)
        try:
            with Runner(env.ApplyEnv) as runner:
                r = runner(p.apply_code, p.sourcelines)
            self.fail('Expected a NameError exception.')
        except exceptions._ExceptionWrapper as e:
            self.assertEquals('NameError', e.clsname)
            self.assertEquals("name 'unknown_function' is not defined", e._msg)
            s =  '  File "<policy:apply>", line 7\n'
            s += '    a = unknown_function()\n'
            s += "NameError: name 'unknown_function' is not defined\n"
            self.assertEquals(s, e.formatted_message)
        except Exception as e:
            msg = 'Expected an _ExceptionWrapper wrapping a NameError exception.'
            msg += '  Instead, found: {0}.'.format(type(e))
            self.fail(msg)
        
        
        
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
class TodayApiFunction_TestCase(base.CeleryManagement_TestCaseBase):
    def test_empty(self):
        T = datetime.time
        D = datetime.date
        dt = api.today()
        self.assertEquals(D.today(), dt.date())
        self.assertEquals(T(hour=0,minute=0,second=0), dt.time())
    
    def test_with_offset0(self):
        T = datetime.time
        D = datetime.date
        dt = api.today(offset_days=0)
        self.assertEquals(D.today(), dt.date())
        self.assertEquals(T(hour=0,minute=0,second=0), dt.time())
    
    def test_with_offset1(self):
        T = datetime.time
        D = datetime.date
        tomorrow = D.today()+datetime.timedelta(days=1)
        dt = api.today(offset_days=1)
        self.assertEquals(tomorrow, dt.date())
        self.assertEquals(T(hour=0,minute=0,second=0), dt.time())
    
    def test_with_offset2(self):
        T = datetime.time
        D = datetime.date
        yesterday = D.today()+datetime.timedelta(days=-1)
        dt = api.today(offset_days=-1)
        self.assertEquals(yesterday, dt.date())
        self.assertEquals(T(hour=0,minute=0,second=0), dt.time())
    
    def test_with_time0(self):
        T = datetime.time
        D = datetime.date
        dt = api.today(time=(0,0))
        self.assertEquals(D.today(), dt.date())
        self.assertEquals(T(hour=0,minute=0,second=0), dt.time())
    
    def test_with_time1(self):
        T = datetime.time
        D = datetime.date
        dt = api.today(time=(1,15))
        self.assertEquals(D.today(), dt.date())
        self.assertEquals(T(1,15,0), dt.time())
    
    def test_with_time2(self):
        T = datetime.time
        D = datetime.date
        dt = api.today(time=(22,4,55,123456))
        self.assertEquals(D.today(), dt.date())
        self.assertEquals(T(22,4,55,123456), dt.time())
    
    def test_with_time3(self):
        T = datetime.time
        D = datetime.date
        # use a list instead of a tuple
        dt = api.today(time=[1,15])
        self.assertEquals(D.today(), dt.date())
        self.assertEquals(T(1,15,0), dt.time())
    
    def test_with_timestr0(self):
        T = datetime.time
        D = datetime.date
        dt = api.today(timestr='0:00')
        self.assertEquals(D.today(), dt.date())
        self.assertEquals(T(hour=0,minute=0,second=0), dt.time())
    
    def test_with_timestr1(self):
        T = datetime.time
        D = datetime.date
        dt = api.today(timestr='18:05')
        self.assertEquals(D.today(), dt.date())
        self.assertEquals(T(18,5,0), dt.time())
    
    def test_with_timestr2(self):
        T = datetime.time
        D = datetime.date
        dt = api.today(timestr='22:00:59')
        self.assertEquals(D.today(), dt.date())
        self.assertEquals(T(22,0,59), dt.time())
    
    def test_with_timestr3(self):
        T = datetime.time
        D = datetime.date
        dt = api.today(timestr='10:00:33.9')
        self.assertEquals(D.today(), dt.date())
        self.assertEquals(T(10,0,33,900000), dt.time())
    
    def test_with_timestr4(self):
        T = datetime.time
        D = datetime.date
        dt = api.today(timestr='10:00:33.123456')
        self.assertEquals(D.today(), dt.date())
        self.assertEquals(T(10,0,33,123456), dt.time())



