import ast

def check_child(node, k, v):
    if k in node._fields:
        if isinstance(v, ast.AST):
            return False
        elif isinstance(v, (tuple,list)):
            if v and not isinstance(v[0], ast.AST):
                return True
            else:
                return False
        else:
            return True
    else:
        return False

def node_children(node):
    # note properties that are not child nodes
    s = ', '.join('{0}: {1}'.format(k,v) for (k,v) 
                  in node.__dict__.iteritems() 
                  if check_child(node,k,v))
    return s

def node_lineinfo(node):
    if isinstance(node, (ast.expr, ast.stmt)):
        return '({0:2}, {1:2})'.format(node.lineno, node.col_offset)
    return ''

class NodeRec(object):
    def __init__(self, node, level):
        self.level = level
        self.name = node.__class__.__name__
        self.fieldvals = node_children(node)
        self.lineinfo = node_lineinfo(node)
        
tab = ' '*2
    
def write_recs(recs):
    maxleft = max([len(r.level*tab)+len(r.name) for r in recs]) + 2
    def rec_to_string(rec):
        indent = rec.level*tab
        w1 = max(maxleft - len(indent), 0)
        return '{0}{1:<{w1}} {3}  {2}\n'.format(indent, rec.name+':', 
                                                rec.fieldvals, rec.lineinfo, 
                                                w1=w1)
    return ''.join(rec_to_string(r) for r in recs)

class PrintVisitor(ast.NodeVisitor):
    def __init__(self):
        super(PrintVisitor, self).__init__()
        self.level = 0
        self.noderecs = []
        
    def visit(self, node):
        rec = NodeRec(node, self.level)
        self.noderecs.append(rec)
        super(PrintVisitor, self).visit(node)
        
    def generic_visit(self, node):
        self.level += 1
        super(PrintVisitor, self).generic_visit(node)
        self.level -= 1
        
class PrintDetailVisitor(object):
    def __init__(self):
        self.level = 0
        self.text = ''
        
    def visit(self, node):
        indent = self.level * tab
        leftside = '{0}{1}:'.format(indent, node.__class__.__name__)
        lineinfo = node_lineinfo(node)
        self.text += '{0:<30}{1}\n'.format(leftside, lineinfo)
        self.level += 1
        self.visit_children(node)
        self.level -= 1
    
    def visit_children(self, node):
        indent = (self.level-1) * tab
        self.level += 1
        for fieldname in node._fields:
            field = getattr(node, fieldname, None)
            if field is None:
                continue
            if isinstance(field, ast.AST):
                field = [field]
            if isinstance(field, list) and field:
                self.text += '{0} -{1}\n'.format(indent, fieldname)
                for f in field:
                    self.visit(f)
        self.level -= 1
        return


def write_ast(tree):
    #visit = PrintDetailVisitor()
    #visit.visit(tree)
    #return visit.text
    
    visit = PrintVisitor()
    visit.visit(tree)
    return write_recs(visit.noderecs)



