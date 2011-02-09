import datetime

from celerymanagementapp.models import DispatchedTask
from djcelery.models import WorkerState

from celerymanagementapp.models import TestModel

from celerymanagementapp import timeutil
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
        self.fieldconv_map = dict((r[0],r[2]) for r in self.field_info)
        ##self.conv_to_python = dict((r[0],r[2]) for r in self.field_info if r[2] is not None)
        ##self.conv_from_python = dict((r[0],r[3]) for r in self.field_info if r[3] is not None)
        
    # def get_conv_to_python(self, fieldname):
        # conv = self.conv_to_python.get(fieldname, None)
        # if not conv:
            # conv = util.noop_conv
        # return conv
        
    # def get_conv_from_python(self, fieldname):
        # conv = self.conv_from_python.get(fieldname, None)
        # if not conv:
            # conv = util.noop_conv
        # return conv
        
    def get_fieldconv(self, fieldname):
        return self.fieldconv_map[fieldname]
        
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
def worker_name_to_id(name):
    return WorkerState.objects.get(hostname=name).id
    
def worker_id_to_name(id):
    return WorkerState.objects.get(id=id).hostname
    
#==============================================================================#
class FieldConv(object):
    """ Class for converting between Python and JSON types. """
    @classmethod
    def to_python(cls):
        def conv(val):
            return val
        return conv
    
    @classmethod
    def from_python(cls):
        def conv(val):
            return val
        return conv
    
    @classmethod
    def interval_to_python(cls):
        return cls.to_python()
        
DefaultConv = FieldConv


class WorkerNameConv(FieldConv):
    @classmethod
    def to_python(cls):
        return worker_name_to_id
    
    @classmethod
    def from_python(cls):
        return worker_id_to_name


class DateConv(FieldConv):
    @classmethod
    def to_python(cls):
        return timeutil.date_to_python
    
    @classmethod
    def from_python(cls):
        return timeutil.date_from_python
    
    @classmethod
    def interval_to_python(cls):
        TD = datetime.timedelta
        def conv(val):
            return TD(milliseconds=val)
        return conv


class DateTimeConv(FieldConv):
    @classmethod
    def to_python(cls):
        return timeutil.datetime_to_python
    
    @classmethod
    def from_python(cls):
        return timeutil.datetime_from_python
    
    @classmethod
    def interval_to_python(cls):
        TD = datetime.timedelta
        def conv(val):
            return TD(milliseconds=val)
        return conv


#==============================================================================#
class JsonTaskModelMap(JsonModelMap):
    model = DispatchedTask
    # field_info:
    #   (field in model, field in query, conv_to_python, conv_from_python)
    field_info = [
        ('name',        'taskname',     DefaultConv),
        ('state',       'state',        DefaultConv),
        ('task_id',     'task_id',      DefaultConv),
        ('worker',      'worker',       WorkerNameConv),
        
        ('runtime',     'runtime',      DefaultConv),
        ('waittime',    'waittime',     DefaultConv),
        ('totaltime',   'totaltime',    DefaultConv),
        
        ('tstamp',      'tstamp',       DateTimeConv),
        ('sent',        'sent',         DateTimeConv),
        ('received',    'received',     DateTimeConv),
        ('started',     'started',      DateTimeConv),
        ('succeeded',   'succeeded',    DateTimeConv),
        ('failed',      'failed',       DateTimeConv),
        
        ('routing_key', 'routing_key',  DefaultConv),
        ('expires',     'expires',      DateTimeConv),
        ('result',      'result',       DefaultConv),
        ('eta',         'eta',          DateTimeConv),
        ]
        
#==============================================================================#
class TestModelModelMap(JsonModelMap):
    model = TestModel
    field_info = [
        ('date',    'date',     DateConv),
        ('datetime','datetime', DateTimeConv),
        ('floatval','floatval', DefaultConv),
        ('intval',  'intval',   DefaultConv),
        ('charval', 'charval',  DefaultConv),
        ('enumval', 'enumval',  DefaultConv),
        ]

#==============================================================================#




