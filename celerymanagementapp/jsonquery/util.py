import datetime
import calendar

from django.db.models import Avg, Max, Min, Sum, Variance

from celerymanagementapp import segmentize
from celerymanagementapp.jsonquery.exception import JsonQueryError

#==============================================================================#
# Conversions

def noop_conv(x):
    return x
    
def date_to_python(val):
    # takes a float and converts it to a python datetime.datetime
    return datetime.date.fromtimestamp(val)

def datetime_to_python(val):
    # takes a float and converts it to a python datetime.datetime
    return datetime.datetime.fromtimestamp(val)
    
def date_from_python(val):
    # takes a python datetime.date and converts it to a float
    tt = val.timetuple()
    unixtime = calendar.timegm(tt)
    return unixtime
    
def datetime_from_python(val):
    # takes a python datetime.datetime and converts it to a float
    tt = val.utctimetuple()
    unixtime = calendar.timegm(tt)
    return unixtime

#==============================================================================#
# Query ops:

class BadFilterOpArguments(JsonQueryError):
    def __init__(self, fieldname):
        msg = 'Incorrect number of arguments for filtering on "{0}".'.format(fieldname)
        super(BadFilterOpArguments, self).__init__(msg)


def process_op_range(fieldname, args):
    if len(args)!=2:
        raise BadFilterOpArguments("range")
    return {'{0}__range'.format(fieldname): (args[0],args[1])}
def process_op_gt(fieldname, args):
    if len(args)!=1:
        raise BadFilterOpArguments(">")
    return {'{0}__gt'.format(fieldname): args[0]}
def process_op_lt(fieldname, args):
    if len(args)!=1:
        raise BadFilterOpArguments("<")
    return {'{0}__lt'.format(fieldname): args[0]}
def process_op_gte(fieldname, args):
    if len(args)!=1:
        raise BadFilterOpArguments(">=")
    return {'{0}__gte'.format(fieldname): args[0]}
def process_op_lte(fieldname, args):
    if len(args)!=1:
        raise BadFilterOpArguments("<=")
    return {'{0}__lte'.format(fieldname): args[0]}
def process_op_eq(fieldname, args):
    if len(args)!=1:
        raise BadFilterOpArguments("==")
    return {'{0}'.format(fieldname): args[0]}
def process_op_ne(fieldname, args):
    if len(args)!=1:
        raise BadFilterOpArguments("!=")
    return {'{0}__ne'.format(fieldname): args[0]}
    
ops_dict = {
    'range':process_op_range,
    '>':    process_op_gt,
    '<':    process_op_lt,
    '>=':   process_op_gte,
    '<=':   process_op_lte,
    '!=':   process_op_eq,
    '==':   process_op_ne,
    }

#==============================================================================#
# Segmentizer stuff:

class AutoLabelSegmentizer(object):
    def __init__(self, fieldname, from_python=noop_conv):
        self.fieldname = fieldname
        self.from_python = from_python
        
    def _make_query_sequence(self, queryset):
        queryseq = segmentize.autolabel_query_sequence(self.fieldname, queryset)
        return queryseq
        
    def __call__(self, queryset):
        queryseq = self._make_query_sequence(queryset)
        conv = self.from_python
        return ( (conv(lbl), queryset.filter(**qargs)) 
                 for (lbl,qargs) in queryseq )

class EachSegmentizer(object):
    def __init__(self, fieldname, from_python=noop_conv):
        self.fieldname = fieldname
        self.from_python = from_python
        
    def _iter_objects(self, queryset):
        return ((getattr(o,self.fieldname), o.pk) for o in queryset)
        
    def __call__(self, queryset):
        it = self._iter_objects(queryset)
        conv = self.from_python
        return ( (conv(lbl), queryset.filter(pk=k)) for (lbl,k) in it )


def segmentizer_method_range(fieldname, args, to_python=noop_conv, from_python=noop_conv):
    query_range = (to_python(args['min']), to_python(args['max']))
    interval = to_python(args['interval'])
    query_sequence = segmentize.range_query_sequence(fieldname, query_range, interval, from_python)
    return segmentize.Segmentizer(query_sequence)
    
def segmentizer_method_values(fieldname, args, to_python=noop_conv, from_python=noop_conv):
    query_sequence = segmentize.basic_query_sequence(fieldname, args)
    return segmentize.Segmentizer(query_sequence)
    
def segmentizer_method_all(fieldname, args, to_python=noop_conv, from_python=noop_conv):
    segmentizer = AutoLabelSegmentizer(fieldname, from_python)
    return segmentizer
    
def segmentizer_method_each(fieldname, args, to_python=noop_conv, from_python=noop_conv):
    segmentizer = EachSegmentizer(fieldname, from_python)
    return segmentizer
    

_segmentizer_method_dict = {
    'range':    segmentizer_method_range,
    'values':   segmentizer_method_values,
    'all':      segmentizer_method_all,
    'each':     segmentizer_method_each,
    }
    
def get_segmethod_dict():
    return _segmentizer_method_dict.copy()
    
#==============================================================================#
# Aggregator stuff:

class CompoundAggregator(object):
    def __init__(self):
        self.aggs = {}
    def __call__(self, queryset):
        ret = {}
        for k,agg in self.aggs.iteritems():
            ret[k] = agg(queryset)
        return ret
    def __setitem__(self, key, aggregator):
        self.aggs.__setitem__(key, aggregator)
        

def aggregator_method_max(fieldname):
    key = '{0}__max'.format(fieldname)
    def _aggregator(queryset):
        return queryset.aggregate(Max(fieldname))[key]
    return _aggregator

def aggregator_method_min(fieldname):
    key = '{0}__min'.format(fieldname)
    def _aggregator(queryset):
        return queryset.aggregate(Min(fieldname))[key]
    return _aggregator

def aggregator_method_average(fieldname):
    key = '{0}__avg'.format(fieldname)
    def _aggregator(queryset):
        return queryset.aggregate(Avg(fieldname))[key]
    return _aggregator

def aggregator_method_variance(fieldname):
    key = '{0}__variance'.format(fieldname)
    def _aggregator(queryset):
        return queryset.aggregate(Var(fieldname))[key]
    return _aggregator

def aggregator_method_sum(fieldname):
    key = '{0}__sum'.format(fieldname)
    def _aggregator(queryset):
        return queryset.aggregate(Sum(fieldname))[key]
    return _aggregator

def aggregator_method_enumerate(fieldname):
    def _aggregator(queryset):
        unique_vals = set(queryset.values_list(fieldname, flat=True))
        return dict( (val, queryset.filter(fieldname=val).count()) 
                     for val in unique_vals )
    return _aggregator

def aggregator_method_count():
    def _aggregator(queryset):
        return queryset.count()
    return _aggregator
        

_aggregator_method_dict = {
    'max':      aggregator_method_max,
    'min':      aggregator_method_min,
    'average':  aggregator_method_average,
    'variance': aggregator_method_variance,
    'sum':      aggregator_method_sum,
    'enumerate':aggregator_method_enumerate,
    }

def get_aggmethod_dict():
    return _aggregator_method_dict.copy()

#==============================================================================#


