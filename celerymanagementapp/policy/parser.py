import ast
import re

from celerymanagementapp.policy import exceptions, tokenlib

# Import token constants directly into this module's namespace.
for v,name in tokenlib.tok_name.iteritems():
    globals()[name] = v
    
#==============================================================================#
def _names(*args):
    assert len(args) > 0
    s = ' '.join(args)
    return list(w for w in s.split())
    
FORBIDDEN_KEYWORDS = _names(
    'def class lambda return yield', # functions, classes
    'import from global del',        # limit name access, modifications
    'for while try except',          # no loops or exceptions
    'exec',)                         # no exec code
FORBIDDEN_NAMES = _names('''__class__ __dict__ __methods__ __members__ __bases__
    __mro__ mro __subclasses__ __new__ __del__ __init__ __getattr__
    __setattr__ __delattr__ __getattribute__ __get__ __set__ __delete__
    __slots__ __metaclass__ __getitem__ __setitem__ __delitem__ __getslice__
    __setslice__ __delslice__ __enter__ __exit__'''
    )
ALLOWED_BUILTINS = _names('''abs all any basestring bin bool bytearray callable
    chr cmp complex dict divmod enumerate filter float format frozenset hash
    help hex id int isinstance issubclass iter len list long map max
    memoryview min next object oct ord pow print range reduce repr reversed
    round set slice sorted str sum tuple unichr unicode xrange zip
    True False None''')
UNASSIGNABLE_NAMES = _names('')

#==============================================================================#
        
def error(msg='', lineno=None, column=None, line=''):
    raise exceptions.SyntaxError(msg, lineno, column, line)

#==============================================================================#
# functions for debugging


#==============================================================================#
class PolicySectionSplitter(object):
    def __init__(self, text):
        self.tokenizer = tokenlib.tokenize(text)
        self.endmarker = (ENDMARKER,None,(-1,-1),(-1,-1),-1)
        self.cur = None
        self.peek = None
        self.nexttok()
        
    #def untokenize(self, iter):
    #    return tokenlib.untokenize(iter)
            
    def nexttok(self):
        try:
            tok = self.tokenizer.next()
            while tok[0] == NL or tok[0] == COMMENT:
                tok = self.tokenizer.next()
            if tok[0]==ENDMARKER:
                self.endmarker = tok
        except StopIteration:
            tok = self.endmarker
        self.cur, self.peek = self.peek, tok
        return self.cur
        
    def match(self, toktype, val=None):
        if self.peek[0] == toktype and (val==None or self.peek[1]==val):
            return self.nexttok()
        else:
            return None
        
    def require(self, toktype, val=None, msg=''):
        if self.peek[0] == toktype and (val==None or self.peek[1]==val):
            return self.nexttok()
        else:
            if not msg:
                tok0 = tokenlib.tok_name[toktype]
                tok1 = tokenlib.tok_name[self.peek[0]]
                msg = 'expected "{0}", found "{1}"'.format(tok0,tok1)
            row,col = self.peek[2]
            line = self.peek[4]
            error(msg, row, col, line)
        
    def grab_content(self):
        toks = []
        indent_level = 0
        peek = self.peek
        while peek[0]!=ENDMARKER and (peek[0]!=DEDENT or indent_level>0):
            if peek[0]==INDENT:
                indent_level += 1
            if peek[0]==DEDENT:
                indent_level -= 1
            toks.append(peek)
            self.nexttok()
            peek = self.peek
        return toks
        
    def __call__(self):
        self.require(NAME, 'policy')
        self.require(COLON)
        self.require(NEWLINE)
        self.require(INDENT)
        ret = self.policy_suite()
        self.require(DEDENT)
        self.require(ENDMARKER)
        return ret
    
    def policy_suite(self):
        schedule = self.schedule()
        conditions = self.conditions()
        apply = self.apply()
        return schedule,conditions,apply
        
    def schedule(self):
        self.require(NAME, 'schedule')
        self.require(COLON)
        self.require(NEWLINE)
        self.require(INDENT)
        toks = self.grab_content()
        self.require(DEDENT)
        return toks
        
    def apply(self):
        self.require(NAME, 'apply')
        self.require(COLON)
        self.require(NEWLINE)
        self.require(INDENT)
        toks = self.grab_content()
        self.require(DEDENT)
        return toks
        
    def conditions(self):
        alltoks = []
        while self.match(NAME, 'condition'):
            self.require(COLON)
            self.require(NEWLINE)
            self.require(INDENT)
            toks = self.grab_content()
            self.require(DEDENT)
            alltoks.append(toks)
        return alltoks

#==============================================================================#
class NodeVisitor(ast.NodeVisitor):
    def __init__(self, text):
        super(NodeVisitor, self).__init__()
        self.text = text

class CheckAssignedNameVisitor(NodeVisitor):
    def __init__(self, text, unassignable_names):
        super(CheckAssignedNameVisitor, self).__init__(text)
        self.unassignable_names = unassignable_names
        
    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Del, ast.AugStore)):
            if node.id in self.unassignable_names:
                row, col = node.lineno, node.col_offset
                line = self.text[row-1]
                msg = 'The name "{0}" may not be assigned to.'.format(node.id)
                error(msg,row,col,line)
        return self.generic_visit(node)


class AssertNoAssignmentsVisitor(NodeVisitor):
    def __init__(self, text):
        super(AssertNoAssignmentsVisitor, self).__init__(text)
    def visit_Assign(self, node):
        row, col = node.lineno, node.col_offset
        line = self.text[row-1]
        msg = 'Assignment is not allowed in this context.'
        error(msg,row,col,line)
    def visit_AugAssign(self, node):
        row, col = node.lineno, node.col_offset
        line = self.text[row-1]
        msg = 'Assignment is not allowed in this context.'
        error(msg,row,col,line)


class AssertNoStatementsVisitor(NodeVisitor):
    def __init__(self, text):
        super(AssertNoStatementsVisitor, self).__init__(text)
    # Only Expr statements are allowed
    def visit(self, node):
        if isinstance(node, ast.stmt) and not isinstance(node, ast.Expr):
            row, col = node.lineno, node.col_offset
            line = self.text[row-1]
            error('No statements allowed in this context.',row,col,line)
        super(AssertNoStatementsVisitor,self).visit(node)


#==============================================================================#
class SectionParser(object):
    # Note: This expects the code to be indented.  It doesn't matter how much, 
    # just as long as it is.
    filename = '<unknown>'
    forbidden_names = set([])
    
    def __init__(self, text):
        self.text = text
        
    def __call__(self, tokens):
        """ tokens is either a list of tokens or a list of lists of tokens. """
        #import debug_help
        if tokens and not isinstance(tokens[0], list):
            ##print 'list of lists!!!'
            tokens = [tokens]
        trees = [self.process_one_subsection(toks) for toks in tokens]
        tree = self.merge_asts(trees)
        #print debug_help.write_ast(tree)
        #print ''
        co = self.compile_ast(tree)
        return co
        
    def process_one_subsection(self, tokens):
        """ tokens is a list of tokens (*not* a list of lists of tokens). """
        #import debug_help
        self.check_tokens(tokens)
        tokens = self.correct_tokens(tokens)
        text = self.assemble_tokens(tokens)
        text = self.correct_text(text)
        tree = self.create_ast(text)
        #print debug_help.write_ast(tree)
        #print ''
        tree = self.fix_linenumbers_ast(tree)
        self.check_ast(tree)
        tree = self.correct_ast(tree)
        #print debug_help.write_ast(tree)
        #print ''
        return tree
    
    
    # the following are all methods that can be overridden in subclasses
    
    def check_tokens(self, tokens):
        badnames = self.forbidden_names
        for ty,val,start,end,ln in tokens:
            if ty==NAME and val in badnames:
                row,col = start
                line = self.text[row-1]
                msg = 'The name "{name}" is not allowed.'.format(name=val)
                error(msg,row,col,line)
            elif ty==KEYWORD and val in badnames:
                row,col = start
                line = self.text[row-1]
                msg = 'The keyword "{name}" is not allowed.'.format(name=val)
                error(msg,row,col,line)
        
    def correct_tokens(self, tokens):
        return tokens
        
    def assemble_tokens(self, tokens):
        return tokenlib.untokenize(tokens)
        
    def correct_text(self, text):
        return 'if True:\n{0}'.format(text)
        
    def create_ast(self, text):
        # TODO: catch syntax errors
        tree = ast.parse(text, self.filename, 'exec')
        
        assert len(tree.body) == 1
        ifnode = tree.body[0]
        if not isinstance(ifnode, ast.If):
            row,col = ifnode.lineno, ifnode.col_offset
            line = self.text[row-1]
            msg = 'Internal error.  Expected an if statement.'
            error(msg,row,col,line)
        
        tree.body = ifnode.body
        return tree
        
    def fix_linenumbers_ast(self, tree):
        # Hack because of Python bug(?).  When creating the tree, some nodes do 
        # not have the _attributes field.
        for node in ast.walk(tree):
            if not hasattr(node, '_attributes'):
                node._attributes = ()
        
        tree = ast.fix_missing_locations(tree)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.stmt, ast.expr)):
                node.lineno -= 1
        
        return tree
        
    def correct_ast(self, tree):
        return tree
        
    def check_ast(self, tree):
        pass
        
    def merge_asts(self, trees):
        assert len(trees) == 1
        return trees[0]
        
    def compile_ast(self, tree):
        compile_mode = 'exec'
        if isinstance(tree, ast.Expression):
            compile_mode = 'eval'
        # TODO: catch syntax errors
        return compile(tree, self.filename, compile_mode)

#------------------------------------------------------------------------------#
class ScheduleSectionParser(SectionParser):
    filename = '<policy:schedule>'
    _forbidden_names = set()
    
    def __init__(self, text):
        super(ScheduleSectionParser, self).__init__(text)
        
    def get_forbidden_names(self):
        return self._forbidden_names | PolicyParser.forbidden_names
    forbidden_names = property(get_forbidden_names)
    
    def check_ast(self, tree):
        for node in tree.body:
            AssertNoStatementsVisitor(self.text).visit(node)
        
    def merge_asts(self, trees):
        assert len(trees) == 1
        tree = ast.Expression(body=trees[0].body[0].value)
        ast.fix_missing_locations(tree)
        return tree
        
    
class ConditionSectionParser(SectionParser):
    # no assignment
    filename = '<policy:condition>'
    _forbidden_names = set()
    
    def __init__(self, text):
        super(ConditionSectionParser, self).__init__(text)
        
    def get_forbidden_names(self):
        return self._forbidden_names | PolicyParser.forbidden_names
    forbidden_names = property(get_forbidden_names)
        
    def correct_ast(self, tree):
        tree = super(ConditionSectionParser,self).correct_ast(tree)
        
        andnodes = [x.value for x in tree.body]
        boolexpr = ast.BoolOp(op=ast.And(), values=andnodes)
        expr = ast.Expr(value=boolexpr)
        tree.body = [expr]
        ast.fix_missing_locations(tree)
        return tree
    
    def check_ast(self, tree):
        for node in tree.body:
            AssertNoStatementsVisitor(self.text).visit(node)
    
    def merge_asts(self, trees):
        exprs = []
        for tree in trees:
            assert len(tree.body) == 1
            exprs.append(tree.body[0])
        
        ornodes = [x.value for x in exprs]
        boolexpr = ast.BoolOp(op=ast.Or(), values=ornodes)
        tree = ast.Expression(body=boolexpr)
        ast.fix_missing_locations(tree)
        return tree
    
class ApplySectionParser(SectionParser):
    filename = '<policy:apply>'
    _forbidden_names = set()
    
    def __init__(self, text):
        super(ApplySectionParser, self).__init__(text)
        
    def get_forbidden_names(self):
        return self._forbidden_names | PolicyParser.forbidden_names
    forbidden_names = property(get_forbidden_names)
    
    def check_ast(self, tree):
        CheckAssignedNameVisitor(self.text, PolicyParser.unassignable_names).visit(tree)


#==============================================================================#
def _get_forbidden_builtins(allowed_builtins):
    import __builtin__
    builtin_names = __builtin__.__dict__.keys()
    return set([name for name in builtin_names if name not in allowed_builtins])


class PolicyParser(object):
    _forbidden_names = set(FORBIDDEN_NAMES)
    _forbidden_keywords = set(FORBIDDEN_KEYWORDS)
    _allowed_builtins = set(ALLOWED_BUILTINS)
    _forbidden_builtins = _get_forbidden_builtins(_allowed_builtins)
    forbidden_names = _forbidden_names | _forbidden_keywords | _forbidden_builtins
    
    unassignable_names = set(UNASSIGNABLE_NAMES)
    
    def __init__(self):
        pass
    
    def parse_schedule(self, tokens, text):
        schedule_parser = ScheduleSectionParser(text)
        return schedule_parser(tokens)
        
    def parse_conditions(self, tokens, text):
        conditions_parser = ConditionSectionParser(text)
        return conditions_parser(tokens)
        
    def parse_apply(self, tokens, text):
        apply_parser = ApplySectionParser(text)
        return apply_parser(tokens)
        
    def __call__(self, text):
        splitter = PolicySectionSplitter(text)
        schedule_toks, condition_toks, apply_toks = splitter()
        lines = text.splitlines()
        
        schedule_code = self.parse_schedule(schedule_toks, lines)
        condition_code = self.parse_conditions(condition_toks, lines)
        apply_code = self.parse_apply(apply_toks, lines)
        
        return schedule_code, condition_code, apply_code
    

#==============================================================================#
def smart_indent(text, sz):
    
    def do_indents(tokenizer):
        indent_next = True
        col_offset = sz
        for tok in tokenizer(text):
            ty,val,start,end,ln = tok
            start = (start[0], start[1]+col_offset)
            # Only if token starts and ends on the same line, is the end column
            # corrected.
            # If the token *does* span more than one line, any following tokens 
            # on the same line do not have their column position corrected.  
            # This ensures the lines appear the same, which will help in error 
            # messages and the like.
            if end[0]==start[0]:
                end = (end[0], end[1]+col_offset)
            else:
                col_offset = 0
            if ty==NEWLINE or ty==NL:
                col_offset = sz
            yield (ty,val,start,end,ln)
    
    tokenize = tokenlib.tokenize
    untokenize = tokenlib.untokenize
    return untokenize(tok for tok in do_indents(tokenize))
    
    
policy_tpl = '''\
policy:
{schedule}
{conditions}
{apply}
'''
section_tpl = '''\
 {section}:
{body}
'''

def combine_section_sources(schedule_src, condition_srcs, apply_src):
    schedule_src = smart_indent(schedule_src, 2)
    condition_srcs = [smart_indent(src, 2) for src in condition_srcs]
    apply_src = smart_indent(apply_src, 2)
    schedule = section_tpl.format(section='schedule', body=schedule_src)
    condition = ''.join(section_tpl.format(section='condition', body=src) for src in condition_srcs)
    apply = section_tpl.format(section='apply', body=apply_src)
    section = policy_tpl.format(schedule=schedule, conditions=condition, apply=apply)
    return section
    

#==============================================================================#






