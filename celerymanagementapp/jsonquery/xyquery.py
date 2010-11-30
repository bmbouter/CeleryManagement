from celerymanagementapp import segmentize
from celerymanagementapp.jsonquery.base import JsonQuery
from celerymanagementapp.jsonquery.exception import JsonQueryError
from celerymanagementapp.jsonquery import util

#==============================================================================#
class SegmentizeSpec(object):
    """Represents the 'segmentize' portion of the json query."""
    _query_name = False
    _method_spec = False
    
    def __init__(self, jsondata):
        self.segmentize_spec = self._extract_spec(jsondata)
    
    def _extract_spec(self, jsondata):
        segmentize_spec = jsondata.get('segmentize', None)
        if segmentize_spec is None:
            msg = "No segmentize directive was found."
            raise JsonQueryError(msg)
        if not isinstance(segmentize_spec, dict):
            msg = "The segmentize directive must be a dictionary."
            raise JsonQueryError(msg)
        return segmentize_spec
        
    def get_query_name(self):
        if not self._query_name:
            self._query_name = self.segmentize_spec.get('field',None)
            if self._query_name is None:
                msg = "The segmentize directive must have a 'field' key."
                raise JsonQueryError(msg)
        return self._query_name
        
    def get_method_spec(self):
        if not self._method_spec:
            self._method_spec = self.segmentize_spec.get('method',None)
            if self._method_spec is None:
                msg = "The segmentize directive must have a 'method' key."
                raise JsonQueryError(msg)
        return self._method_spec
        
    query_name = property(get_query_name)
    method_spec = property(get_method_spec)
    

#==============================================================================#
class AggregateSpec(object):
    """Represents a single aggregation item."""
    _query_name = False
    _method_specs = False
        
    def __init__(self, agg_spec):
        self.agg_spec = self._verify_spec(agg_spec)
        
    def _verify_spec(self, agg_spec):
        if not isinstance(agg_spec, dict):
            msg = "Each aggregate_spec must be a dictionary."
            raise JsonQueryError(msg)
        return agg_spec
        
    def get_query_name(self):
        if not self._query_name:
            self._query_name = self.agg_spec.get('field',None)
            if self._query_name is None:
                msg = "Each aggregate_spec item must have a 'field' key."
                raise JsonQueryError(msg)
        return self._query_name
    
    def get_method_specs(self):
        if not self._method_specs:
            self._method_specs = self.agg_spec.get('methods',None)
            if self._method_specs is None:
                msg = "The aggregate item must have a 'methods' key."
                raise JsonQueryError(msg)
        return self._method_specs
        
    query_name = property(get_query_name)
    method_specs = property(get_method_specs)
    
    
class AggregateSpecList(object):
    """Represents the 'aggregate' portion of the json query."""
    def __init__(self, jsondata):
        self.spec_list = self._extract_spec_list(jsondata)
    
    def _extract_spec_list(self, jsondata):
        spec_list = jsondata.get('aggregate', None)
        if spec_list is None:
            msg = "No aggregate directive was found."
            raise JsonQueryError(msg)
        if not isinstance(spec_list, list):
            msg = "The aggregate directive must be a list."
            raise JsonQueryError(msg)
        return spec_list
        
    def __iter__(self):
        for spec in self.spec_list:
            yield AggregateSpec(spec)
            

#==============================================================================#
class JsonXYQuery(JsonQuery):
    segmentizer_method_dict = util.get_segmethod_dict()
    aggregator_method_dict =  util.get_aggmethod_dict()
    
    def __init__(self, modelmap, jsondata):
        super(JsonXYQuery, self).__init__(modelmap, jsondata)
        self.segspec = SegmentizeSpec(jsondata)
        self.aggspeclist = AggregateSpecList(jsondata)
        
    def build_json_result(self, queryset):
        seg = self._build_segmentizer()
        agg = self._build_aggregator()
        data = segmentize.make_segments(queryset, seg, agg)
        return { 'data': data }
        
    def _get_segmentizer_factory(self, segname):
        # TODO
        segmentizer_factory = self.segmentizer_method_dict.get(segname, None)
        if segmentizer_factory is None:
            msg = "The given segmentize method was not recognized: '{0}'.".format(segname)
            raise JsonQueryError(msg)
        return segmentizer_factory

    def _build_segmentizer(self):
        method_spec = self.segspec.method_spec
        fieldname = self.modelmap.get_fieldname(self.segspec.query_name)
        to_python = self.modelmap.get_conv_to_python(fieldname)
        from_python = self.modelmap.get_conv_from_python(fieldname)
        segmentizer_factory = self._get_segmentizer_factory(method_spec[0])
        method_args = []  if len(method_spec)==1 else  method_spec[1]
        segmentizer = segmentizer_factory(fieldname, method_args, to_python, from_python)
        return segmentizer
        
    def _get_aggregator_factory(self, aggname):
        # TODO
        aggregator_factory = self.aggregator_method_dict.get(aggname, None)
        if aggregator_factory is None:
            msg = "The given aggregate method was not recognized: '{0}'.".format(aggname)
            raise JsonQueryError(msg)
        return aggregator_factory
        
    def _build_method_aggregator(self, fieldname, method_specs):
        method_agg = util.CompoundAggregator()
        for method_spec in method_specs:
            aggregator_factory = self._get_aggregator_factory(method_spec)
            aggregator = aggregator_factory(fieldname)
            method_agg[method_spec] = aggregator
        return method_agg
        
    def _build_aggregator(self):        
        field_agg = util.CompoundAggregator()
        for aggspec in self.aggspeclist:
            if aggspec.query_name=='count':
                field_agg['count'] = util.aggregator_method_count()
            else:
                fieldname = self.modelmap.get_fieldname(aggspec.query_name)
                field_agg[fieldname] = self._build_method_aggregator(fieldname, aggspec.method_specs)
        return field_agg
        