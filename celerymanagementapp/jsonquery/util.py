from django.db.models import Avg, Max, Min, Sum, Variance

from celerymanagementapp import segmentize
from celerymanagementapp.jsonquery.exception import JsonQueryError

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
    def __init__(self, fieldname):
        self.fieldname = fieldname
        
    def _make_query_sequence(self, queryset):
        queryseq = segmentize.autolabel_query_sequence(self.fieldname, queryset)
        return queryseq
        
    def __call__(self, queryset):
        queryseq = self._make_query_sequence(queryset)
        return ( (lbl, queryset.filter(**qargs)) 
                 for (lbl,qargs) in queryseq )


def segmentizer_method_range(fieldname, args):
    query_range = (args['min'],args['max'])
    interval = args['interval']
    query_sequence = segmentize.range_query_sequence(fieldname, query_range, interval)
    return segmentize.Segmentizer(query_sequence)
    
def segmentizer_method_values(fieldname, args):
    query_sequence = segmentize.basic_query_sequence(fieldname, args)
    return segmentize.Segmentizer(query_sequence)
    
def segmentizer_method_all(fieldname, args):
    segmentizer = AutoLabelSegmentizer(fieldname)
    return segmentizer
    
def segmentizer_method_each(fieldname, args):
    # TODO: implement me
    pass

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



