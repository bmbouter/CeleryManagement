from celerymanagementapp.jsonquery import util
from celerymanagementapp.jsonquery.exception import JsonQueryError

#==============================================================================#
class JsonFilter(object):
    def __init__(self, modelmap, jsondata):
        self.modelmap = modelmap
        self.filter_args = self._build_filter(jsondata)
        self.exclude_args = self._build_exclude(jsondata)
        
    def __call__(self, queryset):
        queryset = self._do_filter(queryset)
        queryset = self._do_exclude(queryset)
        return queryset
        
    def _map_query_args(self, fieldname, exp):
        if len(exp)==1:
            return { '{0}'.format(fieldname): exp[0] }
        op = exp[0]
        exp = exp[1:]
        opfunc = util.ops_dict.get(op,None)
        if opfunc is None:
            msg = "Not able to process filter operator: '{0}'".format(op)
            raise JsonQueryError(msg)
        return opfunc(fieldname, exp)
        
    def _build_query_kwarg(self, exp):
        query_name = exp[0]
        fieldname = self.modelmap.get_fieldname(query_name)
        return self._map_query_args(fieldname, exp[1:])
        
    def _build_filter(self, jsondata):
        qargs = {}
        filterexps = jsondata.get('filter', None)
        if filterexps:
            for exp in filterexps:
                qargs.update(self._build_query_kwarg(exp))
        return qargs
        
    def _build_exclude(self, jsondata):
        qargs = {}
        filterexps = jsondata.get('filter', None)
        if filterexps:
            for exp in filterexps:
                qargs.update(self._build_query_kwarg(exp))
        return qargs
        
    def _do_filter(self, queryset):
        return queryset.filter(**self.filter_args)
    def _do_exclude(self, queryset):
        return queryset.exclude(**self.exclude_args)


class JsonQuery(object):
    def __init__(self, modelmap, jsondata):
        self.modelmap = modelmap
        self.filter = JsonFilter(modelmap, jsondata)
        
    def do_filter(self, queryset=None):
        if not queryset:
            queryset = self.modelmap.get_queryset()
        queryset = self.filter(queryset)
        return queryset
        
    def build_json_result(self, queryset):
        raise NotImplementedError
        
    def do_query(self, queryset=None):
        qs = self.do_filter(queryset)
        return self.build_json_result(qs)

#==============================================================================#

    

#==============================================================================#


