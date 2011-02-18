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
        
        def make_field_metadata(item):
            fieldname = item[0]
            queryname = item[1]
            aggmethods = self.aggregation_methods[fieldname]
            segmethods = self.segmentization_methods[fieldname]
            data = { 'type':        item[3], 
                     'allow_null':  item[4], 
                     'segmentize':  {'methods': segmethods,},
                     'aggregate':   {'methods': aggmethods,},
                   }
            return queryname, data
        
        allfields = [r[1] for r in self.field_info]
        self.metadata = dict(make_field_metadata(item) for item in self.field_info)
        self.metadata['count'] = { 'type':        'int', 
                                   'allow_null':  False, 
                                   'segmentize':  {'methods': [],},
                                   'aggregate':   {'methods': ['count'],},
                                 }
        
    def get_metadata(self):
        return self.metadata
        
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
agg_method_common = ['enumerate',]
agg_methods_numeric = ['average', 'min', 'max', 'sum', 'variance',]

class JsonTaskModelMap(JsonModelMap):
    model = DispatchedTask
    field_info = [
    #   (field in model, field in query, FieldConv,     type,           allow_null)
        ('name',        'taskname',     DefaultConv,    'string',       False),
        ('state',       'state',        DefaultConv,    'string',       False),
        ('task_id',     'task_id',      DefaultConv,    'string',       False),
        ('worker',      'worker',       WorkerNameConv, 'string',       False),
        
        ('runtime',     'runtime',      DefaultConv,    'elapsed_time', False),
        ('waittime',    'waittime',     DefaultConv,    'elapsed_time', True),
        ('totaltime',   'totaltime',    DefaultConv,    'elapsed_time', True),
        
        ('tstamp',      'tstamp',       DateTimeConv,   'datetime',     False),
        ('sent',        'sent',         DateTimeConv,   'datetime',     True),
        ('received',    'received',     DateTimeConv,   'datetime',     True),
        ('started',     'started',      DateTimeConv,   'datetime',     True),
        ('succeeded',   'succeeded',    DateTimeConv,   'datetime',     True),
        ('failed',      'failed',       DateTimeConv,   'datetime',     True),
        
        ('routing_key', 'routing_key',  DefaultConv,    'string',       True),
        ('expires',     'expires',      DateTimeConv,   'datetime',     True),
        ('result',      'result',       DefaultConv,    'string',       True),
        ('eta',         'eta',          DateTimeConv,   'datetime',     True),
        ]
    
    aggregation_methods = {
        'name':         ['enumerate',],
        'state':        ['enumerate',],
        'task_id':      [],
        'worker':       ['enumerate',],
        
        'runtime':      agg_methods_numeric,
        'waittime':     agg_methods_numeric,
        'totaltime':    agg_methods_numeric,
        
        'tstamp':       agg_methods_numeric,
        'sent':         agg_methods_numeric,
        'received':     agg_methods_numeric,
        'started':      agg_methods_numeric,
        'succeeded':    agg_methods_numeric,
        'failed':       agg_methods_numeric,
        
        'routing_key':  ['enumerate',],
        'expires':      agg_methods_numeric,
        'result':       ['enumerate',],
        'eta':          agg_methods_numeric,
        }
        
    segmentization_methods = {
        'name':         ['each', 'values', 'all',],
        'state':        ['each', 'values', 'all',],
        'task_id':      ['each', 'values', 'all',],
        'worker':       ['each', 'values', 'all',],
        
        'runtime':      ['each', 'range',],
        'waittime':     ['each', 'range',],
        'totaltime':    ['each', 'range',],
        
        'tstamp':       ['each', 'range',],
        'sent':         ['each', 'range',],
        'received':     ['each', 'range',],
        'started':      ['each', 'range',],
        'succeeded':    ['each', 'range',],
        'failed':       ['each', 'range',],
        
        'routing_key':  ['each', 'values', 'all',],
        'expires':      ['each', 'range',],
        'result':       ['each', 'values', 'all',],
        'eta':          ['each', 'range',],
        }
        
#==============================================================================#
class TestModelModelMap(JsonModelMap):
    model = TestModel
    field_info = [
        ('date',    'date',     DateConv,       'datetime',     True),
        ('datetime','datetime', DateTimeConv,   'datetime',     True),
        ('floatval','floatval', DefaultConv,    'float',        False),
        ('intval',  'intval',   DefaultConv,    'int',          False),
        ('charval', 'charval',  DefaultConv,    'string',       False),
        ('enumval', 'enumval',  DefaultConv,    'string',       False),
        ]
    
    aggregation_methods = {
        'date':         agg_methods_numeric,
        'datetime':     agg_methods_numeric,
        'floatval':     agg_methods_numeric,
        'intval':       agg_methods_numeric,
        
        'charval':      ['enumerate',],
        'enumval':      ['enumerate',],
        }
        
    segmentization_methods = {
        'date':         ['each', 'range',],
        'datetime':     ['each', 'range',],
        'floatval':     ['each', 'range',],
        'intval':       ['each', 'range',],
        
        'charval':      ['each', 'values', 'all',],
        'enumval':      ['each', 'values', 'all',],
        }

#==============================================================================#




