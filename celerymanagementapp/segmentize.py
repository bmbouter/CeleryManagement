"""
The goal here is to take a QuerySet and summarize it into a set of x,y values 
for presentation in a graph.  There are two main steps to this process.

1. First, a QuerySet is broken up into several smaller QuerySets.  Each of 
these represents the data which satisfies some x-value (for instance, the data 
that occurred within a certain time frame, or that date that have a particular 
field value).  This is called Segmentizing, and is performed by a segmentizer.
 
2. Then, each QuerySet segment is processed to produce a single value.  This 
value represents the y-value.  This processes is called Aggregating for its 
similarity to the aggregate method provided by QuerySets--in fact, that 
method is one way to implement an aggregator.

Concepts:

    segmentizer(queryset):
        A callable that takes a QuerySet and returns an iterator over (label, 
        querysubset) tuples.  The 'label' in these tuples should be the x-value 
        which corresponds to the data in the querysubset.  The 'querysubset' 
        should be a subset of the data in the queryset parameter.
        The Segmentizer class fulfills the segmentizer concept.

    aggregator(queryset):
        A callable that summarizes a QuerySet.  The return value will be the 
        y-value corresponding to the given data.
        
Example Usage: 
    (assuming 'queryset' is given and is a django QuerySet.)
    
        states = ['GOOD','INUSE','ERROR']
        szr = Segmentizer(basic_query_sequence('state',states))
        segs = make_segments(queryset, szr, avg_aggregator('runtime'))
    
    This produces a list of tuples.  Each tuple contains a label (from the 
    field 'state', which is one of 'GOOD','INUSE','ERROR') and an average of 
    the 'runtime' fields of the objects that have the label.
    
    One possible return value:
        [('GOOD',2.4),('INUSE',1.1),('ERROR',0.8)]

"""

from django.db.models import Avg

#==============================================================================#
def range_query_sequence(fieldname, range, interval_size, conv=lambda x: x):
    """ Creates a query_sequence over contiguous ranges.  The return value is 
        suitable for use as the query_sequence argument to the Segmentizer 
        class.
       
        fieldname:
            The field on which ranges are to be calculated.
            
        range:
            A tuple with the start and stop values for the overall range.
            
        interval_size:
            The size of each interval to be created.
            
        The first interval will begin at range[0].  The last interval will be 
        the last one which begins before range[1].  No interval will begin at
        or after range[1].
        
        Intervals include the low value but exclude the high value.
    """
    queryname_gte = '{0}__gte'.format(fieldname)
    queryname_lt =  '{0}__lt'.format(fieldname)
    range_min = range[0]
    range_max = range[1]
    range_next = range_min + interval_size
    
    while range_min < range_max:
        label = range_min + interval_size/2
        yield (conv(label), {queryname_gte: range_min, queryname_lt: range_next })
        range_min = range_next
        range_next += interval_size
    
def basic_query_sequence(fieldname, labels, conv=lambda x: x):
    """ Creates a query_sequence over the items in the 'labels' parameter.  The 
        return value is suitable for use as the query_sequence argument to the 
        Segmentizer class.
        
        labels:
            May either be a sequence of values which act both as the label and 
            the value to search for, or a sequence of tuples, each of which 
            contains a label and a value to search for.
            [ label0, label1, label2, ... ]   
              ...or...
            [ (label0, value0), (label1, value1), (label2, value3), ... ]
    """
    queryname = '{0}'.format(fieldname)
    if labels and isinstance(labels[0], tuple):
        return ((conv(label), {queryname: val}) for (label,val) in labels)
    else:
        return ((conv(label), {queryname: label}) for label in labels)
    
def autolabel_query_sequence(fieldname, queryset, conv=lambda x: x):
    """ Creates a query_sequence over all the values for the given field in the 
        given queryset.  The return value is suitable for use as the 
        query_sequence argument to the Segmentizer class.
    """
    queryname = '{0}'.format(fieldname)
    labels = set(queryset.values_list(fieldname, flat=True))
    return ((conv(label), {queryname: label}) for label in labels)


class Segmentizer(object):
    """A function object which fulfills the segmentizer concept."""
    def __init__(self, query_sequence):
        """
            query_sequence:
                An iterable over (label, queryargs) tuples.  The 'queryargs' is 
                a dict which is passed to the QuerySet.filter() method as 
                keyword arguments.  The 'label' is the x-value that corresponds 
                to the data that is returned by the filter method.
        """
        self.queryseq = query_sequence
    
    def __call__(self, queryset):
        """Returns an iterator over tuples of (label, querysubset) pairs.  The 
           'label' is the x-value which corresponds to every item in the 
           'querysubset'."""
        return ( (lbl, queryset.filter(**qargs)) 
                 for (lbl,qargs) in self.queryseq )

#==============================================================================#
def avg_aggregator(fieldname):
    """Returns an aggregator that calculates an average over a QuerySet.  The 
       fieldname parameter is the name of the field to be averaged. """
    def _avg_aggregator(seg):
        return seg.aggregate(Avg(fieldname))['{0}__avg'.format(fieldname)]
    return _avg_aggregator

def count_aggregator():
    """Returns an aggregator that simply returns the number of items in a 
       QuerySet. """
    def _count_aggregator(seg):
        return seg.count()
    return _count_aggregator

#==============================================================================#
def make_segments(queryset, segmentizer, aggregator):
    """ Make segments from the given queryset using the given segmentizer and 
        aggregator callables.  Returns a list of (label,value) pairs, where 
        'label' is generally the x-value and 'value' is generally the y-value.
    """
    return [(label,aggregator(seg)) for (label,seg) in segmentizer(queryset)]

#==============================================================================#


