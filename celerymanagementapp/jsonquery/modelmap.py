from celerymanagementapp.models import DispatchedTask

from celerymanagementapp.models import TestModel

from celerymanagementapp.jsonquery import util
from celerymanagementapp.jsonquery.exception import JsonQueryError


#==============================================================================#
class JsonModelMap(object):
    """ A class which defines the names of a model's fields as well as 
        functions for converting each field's value between Json and Python. 
    """
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
        
    def get_conv_to_python(self, fieldname):
        conv = self.conv_to_python.get(fieldname, None)
        if not conv:
            conv = util.noop_conv
        return conv
        
    def get_conv_from_python(self, fieldname):
        conv = self.conv_from_python.get(fieldname, None)
        if not conv:
            conv = util.noop_conv
        return conv
        
    def get_fieldname(self, query_name):
        """ Retrieve the model field name corresponding to the given 
            query_name. 
        """
        try:
            return self.fieldname_map[query_name]
        except KeyError:
            msg = "Unknown fieldname: '{0}'".format(query_name)
            raise JsonQueryError(msg)
            
    def get_queryset(self):
        """ Return a queryset of all model objects. """
        return self.model.objects.all()
    

#==============================================================================#
class JsonTaskModelMap(JsonModelMap):
    model = DispatchedTask
    # field_info:
    #   (field in model, field in query, conv_to_python, conv_from_python)
    field_info = [
        ('name',        'taskname',     None,   None),
        ('state',       'state',        None,   None),
        ('task_id',     'task_id',      None,   None),
        ('worker',      'worker',       None,   None),
        
        ('runtime',     'runtime',      None,   None),
        ('waittime',    'waittime',     None,   None),
        ('totaltime',   'totaltime',    None,   None),
        
        ('tstamp',      'tstamp', 
            util.datetime_to_python,    util.datetime_from_python),
        ('sent',        'sent',     
            util.datetime_to_python,    util.datetime_from_python),
        ('received',    'received',
            util.datetime_to_python,    util.datetime_from_python),
        ('started',     'started',
            util.datetime_to_python,    util.datetime_from_python),
        ('succeeded',   'succeeded',
            util.datetime_to_python,    util.datetime_from_python),
        ('failed',      'failed',
            util.datetime_to_python,    util.datetime_from_python),
        
        ('routing_key', 'routing_key',  None,   None),
        ('expires',     'expires',
            util.datetime_to_python,    util.datetime_from_python),
        ('result',      'result',       None,   None),
        ('eta',         'eta',
            util.datetime_to_python,    util.datetime_from_python),
        ]
        
#==============================================================================#
class TestModelModelMap(JsonModelMap):
    model = TestModel
    field_info = [
        ('date',    'date',     util.date_to_python, util.date_from_python),
        ('floatval','floatval', None,None),
        ('intval',  'intval',   None,None),
        ('charval', 'charval',  None,None),
        ('enumval', 'enumval',  None,None),
        ]

#==============================================================================#




