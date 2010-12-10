from django.db.models import Avg, Max, Min, Sum, Variance

#==============================================================================#
# Aggregator stuff:

class CompoundAggregator(object):
    """ Aggregator that can own other aggregators.  This allows nesting. """
    def __init__(self):
        self.aggs = {}
    def __call__(self, queryset):
        ret = {}
        for k,agg in self.aggs.iteritems():
            ret[k] = agg(queryset)
        return ret
    def __setitem__(self, key, aggregator):
        self.aggs.__setitem__(key, aggregator)
        

def max(fieldname):
    key = '{0}__max'.format(fieldname)
    def _aggregator(queryset):
        return queryset.aggregate(Max(fieldname))[key]
    return _aggregator

def min(fieldname):
    key = '{0}__min'.format(fieldname)
    def _aggregator(queryset):
        return queryset.aggregate(Min(fieldname))[key]
    return _aggregator

def average(fieldname):
    key = '{0}__avg'.format(fieldname)
    def _aggregator(queryset):
        return queryset.aggregate(Avg(fieldname))[key]
    return _aggregator

def variance(fieldname):
    key = '{0}__variance'.format(fieldname)
    def _aggregator(queryset):
        return queryset.aggregate(Var(fieldname))[key]
    return _aggregator

def sum(fieldname):
    key = '{0}__sum'.format(fieldname)
    def _aggregator(queryset):
        return queryset.aggregate(Sum(fieldname))[key]
    return _aggregator

def enumerate(fieldname):
    def _aggregator(queryset):
        unique_vals = set(queryset.values_list(fieldname, flat=True))
        return dict( (val, queryset.filter(fieldname=val).count()) 
                     for val in unique_vals )
    return _aggregator

def count():
    def _aggregator(queryset):
        return queryset.count()
    return _aggregator
        

# Map from aggregator method name to aggregator method function.
_method_dict = {
    'max':      max,
    'min':      min,
    'average':  average,
    'variance': variance,
    'sum':      sum,
    'enumerate':enumerate,
    }

def method_dict():
    return _method_dict.copy()


#==============================================================================#


