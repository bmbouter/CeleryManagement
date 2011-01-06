import ast
import re

from celerymanagementapp.policy import exceptions, tokenlib, config

# Import token constants directly into this module's namespace.
for v,name in tokenlib.tok_name.iteritems():
    globals()[name] = v

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
# Visitor classes that operate on ASTs.

class NodeVisitor(ast.NodeVisitor):
    def __init__(self, text):
        super(NodeVisitor, self).__init__()
        self.text = text
    def syntax_error(self, node, msg):
        row, col = node.lineno, node.col_offset
        line = self.text[row-1]
        raise exceptions.SyntaxError(msg, row, col, line)
    # Forbidden statements
    def visit_FunctionDef(self, node):
        self.syntax_error(node, 'Function definitions are not allowed.')
    def visit_ClassDef(self, node):
        self.syntax_error(node, 'Class definitions are not allowed.')
    def visit_Return(self, node):
        self.syntax_error(node, 'Return statements are not allowed.')
    def visit_For(self, node):
        self.syntax_error(node, 'For statements are not allowed.')
    def visit_White(self, node):
        self.syntax_error(node, 'While statements are not allowed.')
    def visit_Raise(self, node):
        self.syntax_error(node, 'Raise statements are not allowed.')
    def visit_TryExcept(self, node):
        self.syntax_error(node, 'Try...Except statements are not allowed.')
    def visit_TryFinally(self, node):
        self.syntax_error(node, 'Try...Finally statements are not allowed.')
    def visit_Import(self, node):
        self.syntax_error(node, 'Import statements are not allowed.')
    def visit_ImportFrom(self, node):
        self.syntax_error(node, 'Import...From statements are not allowed.')
    def visit_Exec(self, node):
        self.syntax_error(node, 'Exec statements are not allowed.')
    def visit_Global(self, node):
        self.syntax_error(node, 'Global statements are not allowed.')
    # Forbidden expressions
    def visit_Lambda(self, node):
        self.syntax_error(node, 'Lambda expressions are not allowed.')
    def visit_Yield(self, node):
        self.syntax_error(node, 'Yield expressions are not allowed.')
        
class ApplySectionVisitor(NodeVisitor):
    """ Visits nodes of the 'apply' section and raises an exception if the node 
        is not allowed. """
    def __init__(self, text, unassignable_names):
        super(ApplySectionVisitor, self).__init__(text)
        self.unassignable_names = unassignable_names
    def generic_visit(self, node):
        # visits children of a node
        return super(ApplySectionVisitor, self).generic_visit(node)
    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Del, ast.AugStore)):
            if node.id in self.unassignable_names:
                msg = 'The name "{0}" may not be assigned to nor deleted.'.format(node.id)
                self.syntax_error(node, msg)
        return self.generic_visit(node)
        
class RestrictedNodeVisitor(NodeVisitor):
    """ Allows fewer constructs than NodeVisitor. """
    def __init__(self, text):
        super(RestrictedNodeVisitor, self).__init__(text)
    def visit(self, node):
        if isinstance(node, ast.stmt) and not isinstance(node, ast.Expr):
            self.syntax_error(node, 'No statements are allowed in this context.')
        super(RestrictedNodeVisitor,self).visit(node)
    def visit_Delete(self, node):
        self.syntax_error(node, 'Delete statements are not allowed in this context.')
    def visit_Assign(self, node):
        self.syntax_error(node, 'Assignment is not allowed in this context.')
    def visit_AugAssign(self, node):
        self.syntax_error(node, 'Assignment is not allowed in this context.')
    def visit_If(self, node):
        self.syntax_error(node, 'If statements are not allowed in this context.')

#==============================================================================#
class SectionParser(object):
    # Note: This expects the code to be indented.  It doesn't matter how much, 
    # just as long as it is.
    filename = '<unknown>'
    forbidden_names = None
    unassignable_names = None
    
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
    forbidden_names = config.SCHEDULE_FORBIDDEN_ALL
    
    def __init__(self, text):
        super(ScheduleSectionParser, self).__init__(text)
    
    def check_ast(self, tree):
        for node in tree.body:
            RestrictedNodeVisitor(self.text).visit(node)
        
    def merge_asts(self, trees):
        assert len(trees) == 1
        tree = ast.Expression(body=trees[0].body[0].value)
        ast.fix_missing_locations(tree)
        return tree
        
    
class ConditionSectionParser(SectionParser):
    # no assignment
    filename = '<policy:condition>'
    forbidden_names = config.CONDITION_FORBIDDEN_ALL
    
    def __init__(self, text):
        super(ConditionSectionParser, self).__init__(text)
        
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
            RestrictedNodeVisitor(self.text).visit(node)
    
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
    forbidden_names = config.APPLY_FORBIDDEN_ALL
    unassignable_names = config.APPLY_UNASSIGNABLE_NAMES
    
    def __init__(self, text):
        super(ApplySectionParser, self).__init__(text)
    
    def check_ast(self, tree):
        ApplySectionVisitor(self.text, self.unassignable_names).visit(tree)


#==============================================================================#
def _get_forbidden_builtins(allowed_builtins):
    import __builtin__
    builtin_names = __builtin__.__dict__.keys()
    return set([name for name in builtin_names if name not in allowed_builtins])


class PolicyParser(object):
    #_forbidden_names = set(FORBIDDEN_NAMES)
    #_forbidden_keywords = set(FORBIDDEN_KEYWORDS)
    #_allowed_builtins = set(ALLOWED_BUILTINS)
    #_forbidden_builtins = _get_forbidden_builtins(_allowed_builtins)
    #forbidden_names = _forbidden_names | _forbidden_keywords | _forbidden_builtins
    
    #unassignable_names = set(UNASSIGNABLE_NAMES)
    
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






