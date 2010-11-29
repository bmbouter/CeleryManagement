try:
    from celerymanagementapp.models import DispatchedTask
except ImportError:
    from djcelery.models import TaskState as DispatchedTask

from celerymanagementapp.jsonquery.exception import JsonQueryError


#==============================================================================#
class JsonModelMap(object):
    model = None
    fieldname_map = {}
    conv_to_python = {}
    conv_from_python = {}
    
    # field_info: list of tuples (fieldname, queryname, to_python, from_python)
    field_info = None
    
    def __init__(self):
        self.fieldname_map = dict((r[1],r[0]) for r in self.field_info)
        self.conv_to_python = dict((r[0],r[2]) for r in self.field_info if r[2] is not None)
        self.conv_from_python = dict((r[0],r[3]) for r in self.field_info if r[3] is not None)
    
    def to_python(self, field, val):
        conv = self.conv_to_python.get(field, None)
        if conv:
            return conv(val)
        return val
    
    def from_python(self, field, val):
        conv = self.conv_from_python.get(field, None)
        if conv:
            return conv(val)
        return val
        
    def get_fieldname(self, query_name):
        try:
            return self.fieldname_map[query_name]
        except KeyError:
            msg = "Unknown fieldname: '{0}'".format(query_name)
            raise JsonQueryError(msg)
            
    def get_queryset(self):
        return self.model.objects.all()
    

#==============================================================================#
class JsonTaskModelMap(JsonModelMap):
    model = DispatchedTask
    field_info = [
        ('waittime','waittime',None,None),
        ('runtime','runtime',None,None),
        ('state','state',None,None),
        ('worker','worker',None,None),
        ('taskname','name',None,None),
        ]

#==============================================================================#




