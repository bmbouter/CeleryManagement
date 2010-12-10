
from celerymanagementapp import segmentize
from celerymanagementapp.jsonquery.util import noop_conv

#==============================================================================#
# Segmentizer stuff:

class AutoLabelSegmentizer(object):
    """ Segmentizer that determines the possible label values automatically 
        from the values in the database. 
    """
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
    """ Segmentizer that places each record in the database in its own 
        segment. """
    def __init__(self, fieldname, from_python=noop_conv):
        self.fieldname = fieldname
        self.from_python = from_python
        
    def _iter_objects(self, queryset):
        return ((getattr(o,self.fieldname), o.pk) for o in queryset)
        
    def __call__(self, queryset):
        it = self._iter_objects(queryset)
        conv = self.from_python
        return ( (conv(lbl), queryset.filter(pk=k)) for (lbl,k) in it )


def range(fieldname, args, to_python=noop_conv, from_python=noop_conv):
    query_range = (to_python(args['min']), to_python(args['max']))
    interval = to_python(args['interval'])
    query_sequence = segmentize.range_query_sequence(fieldname, query_range, interval, from_python)
    return segmentize.Segmentizer(query_sequence)
    
def values(fieldname, args, to_python=noop_conv, from_python=noop_conv):
    query_sequence = segmentize.basic_query_sequence(fieldname, args)
    return segmentize.Segmentizer(query_sequence)
    
def all(fieldname, args, to_python=noop_conv, from_python=noop_conv):
    segmentizer = AutoLabelSegmentizer(fieldname, from_python)
    return segmentizer
    
def each(fieldname, args, to_python=noop_conv, from_python=noop_conv):
    segmentizer = EachSegmentizer(fieldname, from_python)
    return segmentizer
    

# Map from segmentizer method name to segmentizer method function.
_method_dict = {
    'range':    range,
    'values':   values,
    'all':      all,
    'each':     each,
    }
    
def method_dict():
    return _method_dict.copy()


#==============================================================================#



