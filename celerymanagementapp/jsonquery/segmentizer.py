
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

def range(fieldname, args, fieldconv):
    """ Segmentizer """
    from_python =       fieldconv.from_python()
    to_python =         fieldconv.to_python()
    interval_to_python= fieldconv.interval_to_python()
    
    query_range = (to_python(args['min']), to_python(args['max']))
    interval = interval_to_python(args['interval'])
    query_sequence = segmentize.range_query_sequence(fieldname, query_range, interval, from_python)
    return segmentize.Segmentizer(query_sequence)
    
def values(fieldname, args, fieldconv):
    from_python =   fieldconv.from_python()
    to_python =     fieldconv.to_python()
    vals = [to_python(arg) for arg in args]
    query_sequence = segmentize.basic_query_sequence(fieldname, vals, from_python)
    return segmentize.Segmentizer(query_sequence)
    
def all(fieldname, args, fieldconv):
    from_python = fieldconv.from_python()
    segmentizer = AutoLabelSegmentizer(fieldname, from_python)
    return segmentizer
    
def each(fieldname, args, fieldconv):
    from_python = fieldconv.from_python()
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



