from celerymanagementapp.jsonquery import filter
from celerymanagementapp.jsonquery.exception import JsonQueryError

#==============================================================================#
class JsonQuery(object):
    """ Base class for performing queries with and returning json data. """
    def __init__(self, modelmap, jsondata):
        self.modelmap = modelmap
        self.filter = filter.JsonFilter(modelmap, jsondata)
        
    def do_filter(self, queryset=None):
        """ Filter the given queryset.  If queryset is None, the filter is 
            executed on all objects in the model. 
        """
        if not queryset:
            queryset = self.modelmap.get_queryset()
        queryset = self.filter(queryset)
        return queryset
        
    def build_json_result(self, queryset):
        """ Perform a query on the given queryset.  This returns Python objects 
            that can be converted to json, such as a dict or list.
        """
        raise NotImplementedError
        
    def do_query(self, queryset=None):
        """ Filter the given queryset (or a queryset of all model objects), 
            perform the query, then return the result as json. 
        """
        qs = self.do_filter(queryset)
        return self.build_json_result(qs)

#==============================================================================#

