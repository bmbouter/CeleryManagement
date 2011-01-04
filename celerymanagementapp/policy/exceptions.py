import __builtin__

_err_tmpl_wcaret = '''\
  File "{file}", line {lineno}
    {line}
    {caret:>{col}}
{clsname}: {msg}
'''
_err_tmpl = '''\
  File "{file}", line {lineno}
    {line}
{clsname}: {msg}
'''


def _error_message(clsname, file, lineno, col, line, msg):
    caret =  ' ' if (col is None or line is None or lineno is None) else '^'
    col =    0 if col is None else col
    file = '<unknown>' if file is None else file
    
    linex = line.lstrip()
    col = max(col-(len(line)-len(linex)), 0)
    linex = linex.rstrip('\n')
    
    lineno = '???' if lineno is None else lineno
    if caret=='^':
        return _err_tmpl_wcaret.format(file=file, line=linex, caret=caret, 
                                       col=col, msg=msg, lineno=lineno, 
                                       clsname=clsname)
    else:
        return _err_tmpl.format(file=file, line=linex, caret=caret, 
                                       col=col, msg=msg, lineno=lineno, 
                                       clsname=clsname)


class BaseException(__builtin__.Exception):
    pass


class Error(BaseException):
    clsname = 'PolicyError'
    def __init__(self, msg='', lineno=None, column=None, line='', file=None):
        self.lineno = lineno
        self.column = column
        self.line = line
        msg = _error_message(clsname=self.clsname, file=file, lineno=lineno, 
                             col=column, line=line, msg=msg)
        self.formatted_message = msg
        super(Error, self).__init__('\n{0}'.format(msg))
        
    def __unicode__(self):
        return u'\n'+self.formatted_message
        
    def __str__(self):
        return '\n'+self.formatted_message
        
def ExceptionWrapper(exctype, *args, **kwargs):
    class _ExceptionWrapper(Error):
        clsname = exctype.__name__
        def __init__(self, *args, **kwargs):
            super(_ExceptionWrapper, self).__init__(*args, **kwargs)
    _ExceptionWrapper.__name__ = exctype.__name__
    return _ExceptionWrapper(*args, **kwargs)
        

class SyntaxError(Error):
    clsname = 'PolicySyntaxError'
    def __init__(self, msg, lineno=None, column=None, line=''):
        super(SyntaxError, self).__init__(msg=msg, lineno=lineno, 
                                          column=column, line=line)
        
def error(msg='', *args, **kwargs):
    raise SyntaxError(msg, *args, **kwargs)


