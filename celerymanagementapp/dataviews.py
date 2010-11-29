import json

from django.http import HttpResponse

from celerymanagementapp.jsonquery.xyquery import JsonXYQuery
from celerymanagementapp.jsonquery.modelmap import JsonTaskModelMap


def task_xy_dataview(request):
    #mimetype = 'application/json'
    mimetype = 'text/plain'
    #rawjson = request.POST['query']
    
    query = {
        #'segmentize': {
        #    'field': 'state',
        #    'method': ['all'],
        #},
        'segmentize': {
            'field': 'runtime',
            'method': ['range',{'min': 0.00002, 'max': 0.0006, 'interval':0.00005}]
        },
        #'aggregate': [
        #    {
        #        'field' : 'count',
        #    },
        #],
        'aggregate': [
            {
                'field' : 'count',
            },
            #{
            #    'field' : 'waittime',
            #    'methods': ['average']
            #},
        ],
    }
    
    rawjson = json.dumps(query)
    
    jsondata = json.loads(rawjson)
    
    xyquery = JsonXYQuery(JsonTaskModelMap(), jsondata)
    qs = xyquery.do_filter()
    jsondata = xyquery.build_json_result(qs)
    
    rawjson = json.dumps(jsondata, indent=2)  # remove 'indent' when done testing
    return HttpResponse(rawjson, mimetype=mimetype)



