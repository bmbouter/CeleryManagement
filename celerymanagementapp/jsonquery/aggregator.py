from django.db.models import Avg, Max, Min, Sum, Variance

#==============================================================================#
# Aggregator stuff:

class CompoundAggregator(object):
    """ Aggregator that can own other aggregators.  This allows nesting. """
    def __init__(self):
        self.aggs = {}
        
    def __call__(self, queryset):
        """ The aggregator function.  This simply calls its owned aggregators 
            and places the results in a dictionary. 
        """
        ret = {}
        for k,agg in self.aggs.iteritems():
            ret[k] = agg(queryset)
        return ret
        
    def __setitem__(self, key, aggregator):
        """ Add a new nested aggregator to the compound aggregator. """
        self.aggs.__setitem__(key, aggregator)
        
class ListAggregator(object):
    """ Aggregator that can own other aggregators.  This allows nesting. """
    def __init__(self):
        self.aggs = []
        
    def __call__(self, queryset):
        return [agg(queryset) for agg in self.aggs]
        
    def append(self, aggregator):
        self.aggs.append(aggregator)
        
    def extend(self, aggregators):
        self.aggs.extend(aggregators)
        

def max(fieldname, *args):
    """ Return a max value aggregator function.  The returned function can be 
        used to aggregate a queryset on the maximum value found in the field 
        *fieldname*. 
    """
    key = '{0}__max'.format(fieldname)
    def _aggregator(queryset):
        return queryset.aggregate(Max(fieldname))[key]
    return _aggregator

def min(fieldname, *args):
    """ Return a min value aggregator function.  The returned function can be 
        used to aggregate a queryset on the minimum value found in the field 
        *fieldname*. 
    """
    key = '{0}__min'.format(fieldname)
    def _aggregator(queryset):
        return queryset.aggregate(Min(fieldname))[key]
    return _aggregator

def average(fieldname, *args):
    """ Return an average aggregator function.  The returned function can be 
        used to aggregate a queryset on the average of the values found in the 
        field *fieldname*. 
    """
    key = '{0}__avg'.format(fieldname)
    def _aggregator(queryset):
        return queryset.aggregate(Avg(fieldname))[key]
    return _aggregator

def variance(fieldname, *args):
    """ Return a variance value aggregator function.  The returned function can 
        be used to aggregate a queryset on the variance of the values found in 
        the field *fieldname*. 
    """
    key = '{0}__variance'.format(fieldname)
    def _aggregator(queryset):
        return queryset.aggregate(Var(fieldname))[key]
    return _aggregator

def sum(fieldname, *args):
    """ Return a sum aggregator function.  The returned function can be used to 
        aggregate a queryset on the sum of the values found in the field 
        *fieldname*. 
    """
    key = '{0}__sum'.format(fieldname)
    def _aggregator(queryset):
        return queryset.aggregate(Sum(fieldname))[key]
    return _aggregator

def enumerate(fieldname, from_python, *args):
    """ Return an enumerate aggregator function.  The returned function can be 
        used to aggregate a queryset on the number of occurrences of each value 
        in the field *fieldname*. 
    """
    def _aggregator(queryset):
        unique_vals = set(queryset.values_list(fieldname, flat=True))
        return dict( (from_python(val), queryset.filter(**{fieldname: val}).count()) 
                     for val in unique_vals )
    return _aggregator

def count():
    """ Return a count aggregator function.  It returns the size of a given 
        queryset. 
    """
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


