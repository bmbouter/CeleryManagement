import sys
import traceback

from celerymanagementapp.policy import parser, exceptions, env

_policyparser = parser.PolicyParser()


#==============================================================================#
class Runner(object):
    def __init__(self, globals, locals):
        self.globals = globals
        self.locals = locals
        # the following are used for testing
        self.last_globals = {}
        self.last_locals = {}
        
    def __call__(self, code, text):
        globals = self.globals.copy() 
        locals = self.locals.copy() 
        try:
            r = eval(code, globals, locals)
        except exceptions.StaticException:
            # If the exception is a static Policy exception, reraise it.
            raise
        except exceptions.Exception as e:
            # Other Policy exceptions need line information.
            exctype, excval, tb = sys.exc_info()
            line, lineno, filename = exceptions.policy_traceback_info(text, tb)
            e.set_policy_context(lineno=lineno, line=line, file=file)
            raise
        except Exception as e:
            # If it came from a policy, wrap the exception...
            exctype, excval, tb = sys.exc_info()
            line, lineno, filename = exceptions.policy_traceback_info(text, tb)
            if line:
                EW = exceptions.ExceptionWrapper
                raise EW(exctype, msg=e.message, lineno=lineno, 
                         line=text[lineno-1], file=filename)
            # ...otherwise re-raise the exception.
            else:
                raise
        finally:
            self.last_globals = globals
            self.last_locals = locals
        return r
        
_schedule_runner = Runner(globals=env.SCHEDULE_GLOBALS, 
                          locals=env.SCHEDULE_LOCALS)
_condition_runner = Runner(globals=env.CONDITION_GLOBALS, 
                           locals=env.CONDITION_LOCALS)
_apply_runner = Runner(globals=env.APPLY_GLOBALS, 
                       locals=env.APPLY_LOCALS)

#==============================================================================#
class Policy(object):
    def __init__(self, source=None, schedule_src=None, condition_srcs=None, apply_src=None, id=None, name=None):
        """ Create a policy object. 
        
            If the 'source' arg is not provided, then all three 'schedule_src', 
            'condition_srcs', 'apply_src' must be provided.
            
            The 'name' argument must be present when creating new Policies that 
            do not exist in the database.
            
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
        self.id = id
        self._initself()
        self._compile_src(source, schedule_src, condition_srcs, apply_src)
        self.name = name
        
    def reinit(self, source, name):
        """ Re-initializes the policy.  This is used """
        assert source is not None
        assert name is not None
        self._initself()
        self._compile_src(source=source)
        self.name = name
        
    def _initself(self):
        self.sourcelines = []   # The policy source code as a list of lines.  
                                # Used to display context when errors occur.
        self._source = None     # The source code as a string.
        self.condition_code = None  # the compiled condition-section code
        self.apply_code = None  # the compiled apply-section code
        self.schedule = None  # the result of running the schedule-section code
        
    def _compile_src(self, source=None, schedule_src=None, condition_srcs=None, apply_src=None):
        #if source is None:
        self._source = source or parser.combine_section_sources(schedule_src, condition_srcs, apply_src)
        self.sourcelines = self._source.splitlines()
        ret = _policyparser(self._source)
        schedule_code, self.condition_code, self.apply_code = ret
        self.schedule = _schedule_runner(schedule_code, self.sourcelines)
        
    def run_condition(self):
        return _condition_runner(self.condition_code, self.sourcelines)
        
    def run_apply(self):
        return _apply_runner(self.apply_code, self.sourcelines)
        
    def is_due(self, last_run_time):
        return self.schedule.is_due(last_run_time)
        
    def getsource(self):
        return self._source
    source = property(getsource)


#==============================================================================#
def combine_sources(source=None, schedule_src=None, condition_srcs=None, apply_src=None):
    return source or parser.combine_section_sources(schedule_src, condition_srcs, apply_src)

def check_source(source):
    """ Throws an exception on error.  If no exception was thrown, the 
        compilation was successful.
    """
    _policyparser(source)
    return True























