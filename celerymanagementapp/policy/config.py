import __builtin__
ALL_BUILTINS = set(__builtin__.__dict__.keys())

#==============================================================================#
# Name setup for policies.  A setting which applies to all sections will be 
# merged with the appropriate settings for specific sections.  For instance, 
# FORBIDDEN_KEYWORDS will be merged into SCHEDULE_FORBIDDEN_KEYWORDS, 
# CONDITION_FORBIDDEN_KEYWORDS, and APPLY_FORBIDDEN_KEYWORDS.
#==============================================================================#
def _names(*args):
    """ Splits strings at whitespace boundaries.  Returns a list of the 
        resulting words. """
    assert len(args) > 0
    s = ' '.join(args)
    return set(w for w in s.split())
    
#==============================================================================#
FORBIDDEN_KEYWORDS = _names(
    'def class lambda return yield', # functions, classes
    'import from global del',        # limit name access, modifications
    'while try except',          # no loops or exceptions
    'exec',)                         # no exec code
FORBIDDEN_NAMES = _names('''__class__ __dict__ __methods__ __members__ __bases__
    __mro__ mro __subclasses__ __new__ __del__ __init__ __getattr__
    __setattr__ __delattr__ __getattribute__ __get__ __set__ __delete__
    __slots__ __metaclass__ __getitem__ __setitem__ __delitem__ __getslice__
    __setslice__ __delslice__ __enter__ __exit__ __builtin__ __builtins__'''
    )
ALLOWED_BUILTINS = _names('''abs all any basestring bin bool bytearray callable
    chr cmp complex dict divmod enumerate filter float format frozenset hash
    help hex id int isinstance issubclass iter len list long map max
    memoryview min next object oct ord pow print range reduce repr reversed
    round set slice sorted str sum tuple unichr unicode xrange zip
    True False None''')
UNASSIGNABLE_NAMES = _names('')

#------------------------------------------------------------------------------#
SCHEDULE_FORBIDDEN_KEYWORDS = _names('')
SCHEDULE_FORBIDDEN_NAMES = _names('')
SCHEDULE_ALLOWED_BUILTINS = _names('')

CONDITION_FORBIDDEN_KEYWORDS = _names('')
CONDITION_FORBIDDEN_NAMES = _names('')
CONDITION_ALLOWED_BUILTINS = _names('')

APPLY_FORBIDDEN_KEYWORDS = _names('')
APPLY_FORBIDDEN_NAMES = _names('')
APPLY_ALLOWED_BUILTINS = _names('')
APPLY_UNASSIGNABLE_NAMES = _names('')

#==============================================================================#
# Merge with sections.
SCHEDULE_FORBIDDEN_KEYWORDS |= FORBIDDEN_KEYWORDS
SCHEDULE_FORBIDDEN_NAMES |= FORBIDDEN_NAMES
SCHEDULE_ALLOWED_BUILTINS |= ALLOWED_BUILTINS

CONDITION_FORBIDDEN_KEYWORDS |= FORBIDDEN_KEYWORDS
CONDITION_FORBIDDEN_NAMES |= FORBIDDEN_NAMES
CONDITION_ALLOWED_BUILTINS |= ALLOWED_BUILTINS

APPLY_FORBIDDEN_KEYWORDS |= FORBIDDEN_KEYWORDS
APPLY_FORBIDDEN_NAMES |= FORBIDDEN_NAMES
APPLY_ALLOWED_BUILTINS |= ALLOWED_BUILTINS
APPLY_UNASSIGNABLE_NAMES |= UNASSIGNABLE_NAMES

#==============================================================================#
SCHEDULE_FORBIDDEN_BUILTINS = ALL_BUILTINS - SCHEDULE_ALLOWED_BUILTINS
CONDITION_FORBIDDEN_BUILTINS = ALL_BUILTINS - CONDITION_ALLOWED_BUILTINS
APPLY_FORBIDDEN_BUILTINS = ALL_BUILTINS - APPLY_ALLOWED_BUILTINS

#==============================================================================#
SCHEDULE_FORBIDDEN_ALL = ( SCHEDULE_FORBIDDEN_KEYWORDS 
                         | SCHEDULE_FORBIDDEN_NAMES 
                         | SCHEDULE_FORBIDDEN_BUILTINS)
CONDITION_FORBIDDEN_ALL = ( CONDITION_FORBIDDEN_KEYWORDS 
                          | CONDITION_FORBIDDEN_NAMES 
                          | CONDITION_FORBIDDEN_BUILTINS)
APPLY_FORBIDDEN_ALL = ( APPLY_FORBIDDEN_KEYWORDS 
                      | APPLY_FORBIDDEN_NAMES 
                      | APPLY_FORBIDDEN_BUILTINS)

#==============================================================================#



