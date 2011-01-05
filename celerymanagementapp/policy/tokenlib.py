# This module is named 'tokenlib' to prevent conflicts with the standard 
# module 'token'.

# Note: tokenize also includes the names from the 'token' module.
import tokenize as _tokenize
import re
import keyword

# Import token constants directly into this module's namespace.
for name,v in _tokenize.__dict__.iteritems():
    if name==name.upper() and isinstance(v, int):
        globals()[name] = v

#==============================================================================#
# The tokenize module parses these all as 'OP'.
_op_tokens_lookup = {
    '(': LPAR,
    ')': RPAR,
    '[': LSQB,
    ']': RSQB,
    
    ';': SEMI,
    ':': COLON,
    ',': COMMA,
    '.': DOT,
    
    '+': PLUS,
    '-': MINUS,
    '*': STAR,
    '/': SLASH,
    '%': PERCENT,
    
    '|': VBAR,
    '&': AMPER,
    '~': TILDE,
    '^': CIRCUMFLEX,
    '`': BACKQUOTE,
    
    '=': EQUAL,
    '+=': PLUSEQUAL,
    '-=': MINEQUAL,
    '*=': STAREQUAL,
    '/=': SLASHEQUAL,
    '%=': PERCENTEQUAL,
    
    '|=': VBAREQUAL,
    '&=': AMPEREQUAL,
    '^=': CIRCUMFLEXEQUAL,
    
    '==': EQEQUAL,
    '!=': NOTEQUAL,
    '<=': LESSEQUAL,
    '>=': GREATEREQUAL,
    '<': LESS,
    '>': GREATER,
    
    '**': DOUBLESTAR,
    '//': DOUBLESLASH,
    '>>': RIGHTSHIFT,
    '<<': LEFTSHIFT,
    
    '**=': DOUBLESTAREQUAL,
    '//=': DOUBLESLASHEQUAL,
    '>>=': RIGHTSHIFTEQUAL,
    '<<=': LEFTSHIFTEQUAL,
    }
    
KEYWORD = N_TOKENS
N_TOKENS += 1

tok_name = _tokenize.tok_name.copy()
tok_name[KEYWORD] = 'KEYWORD'

#==============================================================================#
_assigns = frozenset((EQUAL,PLUSEQUAL,MINEQUAL,STAREQUAL,SLASHEQUAL,PERCENTEQUAL,))

def is_assignmentop(toktype):
    return toktype in _assigns
    
#==============================================================================#
_re_lines = re.compile(r'.*(\r\n|\n|\Z)')
    
class StringReadline(object):
    def __init__(self, s):
        self.match_iter = _re_lines.finditer(s)
        self.rest = ''
    def readline(self, size=0):
        if self.rest:
            if size and size < len(self.rest):
                s, self.rest = self.rest[:size], self.rest[size:]
            else:
                s, self.rest = self.rest, ''
        else:
            try:
                s = self.match_iter.next().group()
                if size and size < len(s):
                    s, self.rest = s[:size], s[size:]
            except StopIteration:
                s = ''
        return s
    
def tokenize(readline):
    if hasattr(readline, 'readline'):
        readline = getattr(readline, 'readline')
    elif isinstance(readline, basestring):
        readline = StringReadline(readline).readline
    for tok in _tokenize.generate_tokens(readline):
        ty,val,start,end,ln = tok
        if ty==OP:
            ty = _op_tokens_lookup[val]
        if ty==NAME and keyword.iskeyword(val):
            ty = KEYWORD
        ## skip COMMENTs
        #elif ty==COMMENT:
        #    continue
        yield (ty,val,start,end,ln)
        

#==============================================================================#
def untokenize(iterable):
    prev_row = 1
    prev_col = 0
    toks = []
    
    def insert_space(start):
        row, col = start
        assert row >= prev_row
        row_diff = row - prev_row
        if row_diff:
            toks.append('\n' * row_diff)
            toks.append(' ' * col)
            return
        col_diff = col - prev_col
        if col_diff:
            toks.append(' ' * col_diff)
    
    for tok in iterable:
        ty,val,start,end,ln = tok
        insert_space(start)
        toks.append(val)
        prev_row, prev_col = end
        if ty in (NEWLINE,NL):
            prev_row += 1
            prev_col = 0
            
    return ''.join(toks)


#==============================================================================#
