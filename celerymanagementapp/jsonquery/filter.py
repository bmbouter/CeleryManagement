from django.db.models import Q

from celerymanagementapp.jsonquery.exception import JsonQueryError

#==============================================================================#
class BadFilterOpArguments(JsonQueryError):
    """ Exception which indicates there was an error in the number of 
        arguments. 
    """
    def __init__(self, fieldname):
        msg = 'Incorrect number of arguments for filtering on "{0}".'.format(fieldname)
        super(BadFilterOpArguments, self).__init__(msg)


def process_op_range(fieldname, args):
    """ op: [field, 'range', min, max] """
    if len(args)!=2:
        raise BadFilterOpArguments("range")
    return [], {'{0}__range'.format(fieldname): (args[0],args[1])}
    
def process_op_gt(fieldname, args):
    """ op: [field, '>', val] """
    if len(args)!=1:
        raise BadFilterOpArguments(">")
    return [], {'{0}__gt'.format(fieldname): args[0]}
    
def process_op_lt(fieldname, args):
    """ op: [field, '<', val] """
    if len(args)!=1:
        raise BadFilterOpArguments("<")
    return [], {'{0}__lt'.format(fieldname): args[0]}
    
def process_op_gte(fieldname, args):
    """ op: [field, '>=', val] """
    if len(args)!=1:
        raise BadFilterOpArguments(">=")
    return [], {'{0}__gte'.format(fieldname): args[0]}
    
def process_op_lte(fieldname, args):
    """ op: [field, '<=', val] """
    if len(args)!=1:
        raise BadFilterOpArguments("<=")
    return [], {'{0}__lte'.format(fieldname): args[0]}
    
def process_op_eq(fieldname, args):
    """ op: [field, '==', val], or [field, val] """
    if len(args)!=1:
        raise BadFilterOpArguments("==")
    return [], {fieldname: args[0]}
    
def process_op_ne(fieldname, args):
    """ op: [field, '!=', val] """
    if len(args)!=1:
        raise BadFilterOpArguments("!=")
    return [~Q(**{fieldname: args[0]})], {}
    
# Map from op name to corresponding op function.
ops_dict = {
    'range':process_op_range,
    '>':    process_op_gt,
    '<':    process_op_lt,
    '>=':   process_op_gte,
    '<=':   process_op_lte,
    '!=':   process_op_ne,
    '==':   process_op_eq,
    }


#==============================================================================#
class QueryArgs(object):
    def __init__(self):
        self.args = []
        self.kwargs = {}
        
    def update(self, args, kwargs):
        self.args.extend(args)
        self.kwargs.update(kwargs)
        
    def __str__(self):
        return 'args: {0},  kwargs: {1}'.format(self.args, self.kwargs)
    
    

class JsonFilter(object):
    """ Function object for filtering a Django QuerySet using data from a Json 
        query.
        
        This processes the 'filter' and 'exclude' keys in a jsondata dict.
    """
    def __init__(self, modelmap, jsondata):
        """ Create a JsonFilter object.
            
            modelmap:
                An instance of a class derived from 
                jsonquery.modelmap.JsonModelMap.  This defines which fields are 
                present in the underlying model and the functions for 
                converting from Json format to Python objects, and vice versa.
                
            jsondata:
                A Python dict.  The keys 'filter' and 'exclude' are used by 
                JsonFilter--all others are ignored.  Both keys are optional; if 
                neither is present, no filtering will be performed.
        """
        self.modelmap = modelmap
        self.filter_args = self._build_filter(jsondata)
        self.exclude_args = self._build_exclude(jsondata)
        
    def __call__(self, queryset):
        """ Use the JsonFilter on a queryset.  The resulting filtered queryset 
            is returned. """
        queryset = self._do_filter(queryset)
        queryset = self._do_exclude(queryset)
        return queryset
        
    def _map_query_args(self, fieldname, exp):
        """ Convert a fieldname and the trailing portion of a single filter 
            expression into equivalent Django QuerySet positional and keyword 
            arguments.
        """
        if len(exp)==1:
            opfunc = process_op_eq
        else:
            op = exp[0]
            exp = exp[1:]
            opfunc = ops_dict.get(op,None)
            if opfunc is None:
                msg = "Not able to process filter operator: '{0}'".format(op)
                raise JsonQueryError(msg)
        conv = self.modelmap.get_conv_to_python(fieldname)
        return opfunc(fieldname, map(conv,exp))
        
    def _build_query_kwarg(self, exp):
        """ Convert a single filter expression from a Json query into 
            equivalent Django QuerySet keyword arguments.  The return value is 
            a tuple containing positional arguments and keyword arguments.
        """
        query_name = exp[0]
        fieldname = self.modelmap.get_fieldname(query_name)
        return self._map_query_args(fieldname, exp[1:])
        
    def _build_filter(self, jsondata):
        """ Convert the 'filter' values in the given jsondata to the format 
            expected by the Django QuerySet.filter() method.  The return value 
            is a dict whose contents should be passed to QuerySet.filter() as 
            keyword arguments. 
        """
        args = QueryArgs()
        filterexps = jsondata.get('filter', None)
        if filterexps:
            for exp in filterexps:
                args.update(*self._build_query_kwarg(exp))
        return args
        
    def _build_exclude(self, jsondata):
        """ Convert the 'exclude' values in the given jsondata to the format 
            expected by the Django QuerySet.exclude() method.  The return value 
            is a dict whose contents should be passed to QuerySet.exclude() as 
            keyword arguments. 
        """
        args = QueryArgs()
        filterexps = jsondata.get('exclude', None)
        if filterexps:
            for exp in filterexps:
                args.update(*self._build_query_kwarg(exp))
        return args
        
    def _do_filter(self, queryset):
        """ Perform a filter operation on the given queryset.  Return the 
            resulting queryset. 
        """
        return queryset.filter(*self.filter_args.args, **self.filter_args.kwargs)
        
    def _do_exclude(self, queryset):
        """ Perform an exclude operation on the given queryset.  Return the 
            resulting queryset. 
        """
        return queryset.exclude(*self.exclude_args.args, **self.exclude_args.kwargs)

#==============================================================================#





