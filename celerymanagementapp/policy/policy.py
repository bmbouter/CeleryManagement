import sys
import traceback

from celerymanagementapp.policy import parser, exceptions

_policyparser = parser.PolicyParser()


class Runner(object):
    def __init__(self, globals, locals):
        self.globals = globals
        self.locals = locals
        
    def __call__(self, code, text):
        # TODO: catch and reformat exceptions
        globals = self.globals.copy()
        locals = self.locals.copy()
        try:
            r = eval(code, globals, locals)
        except exceptions.BaseException:
            raise
        except Exception as e:
            exctype, excval, tb = sys.exc_info()
            fmttb = traceback.extract_tb(tb)
            filename, lineno, funcname, txt_ = fmttb[-1]
            if filename.startswith('<policy:'):
                print '[{0}]: {1}'.format(lineno, text[lineno-1])
                EW = exceptions.ExceptionWrapper
                raise EW(exctype, msg=e.message, lineno=lineno, 
                         line=text[lineno-1], file=filename)
            else:
                raise
        return r
        
_runner = Runner(globals={}, locals={})

class Policy(object):
    def __init__(self, source=None, schedule_src=None, condition_srcs=None, apply_src=None, id=None):
        """ Create a policy object. 
        
            If the 'source' arg is not provided, then all three 'schedule_src', 
            'condition_srcs', 'apply_src' must be provided.
            
            source:
                The source text for the policy.
                
            schedule_src:
                The source of the policy's schedule section.  This should 
                contain only the section content--the 'schedule:' heading must 
                not be present.
                
            condition_srcs:
                A sequence containing the sources of the policy's condition 
                sections.  These sources should contain only the section 
                content--the 'condition:' headings must not be present.  The 
                sequence may be empty.
                
            apply_src:
                The source of the policy's apply section.  This should 
                contain only the section content--the 'apply:' heading must 
                not be present.
                
            id:
                The policy's database id.  If provided, the policy must exist 
                in the database and have this value as it's primary key.  Do 
                not set this value unless you know what you are doing.
        """
        self._compile_src(source, schedule_src, condition_srcs, apply_src)
        self.id = id
        
    def reinit(self, source):
        assert source is not None
        self._compile_src(source=source)
        
    def _compile_src(self, source=None, schedule_src=None, condition_srcs=None, apply_src=None):
        if source is None:
            source = parser.combine_section_sources(schedule_src, condition_srcs, apply_src)
        self.source = source.splitlines()
        ret = _policyparser(source)
        self.schedule_code, self.condition_code, self.apply_code = ret
        self._init_schedule()
         
    def _init_schedule(self):
        self.schedule = _runner(self.schedule_code, self.source)
        
    def run_condition(self):
        return _runner(self.condition_code, self.source)
        
    def run_apply(self):
        return _runner(self.apply_code, self.source)
        
    def next_run_time(self, last_run_time):
        pass



























