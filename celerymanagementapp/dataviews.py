import json

from django.http import HttpResponse

from celerymanagementapp.jsonquery.xyquery import JsonXYQuery
from celerymanagementapp.jsonquery.modelmap import JsonTaskModelMap


def _get_json(request):
    rawjson = request.raw_post_data
    return json.loads(rawjson)
    
def _json_response(jsondata):
    rawjson = json.dumps(jsondata)
    return HttpResponse(rawjson, mimetype='application/json')


def task_xy_dataview(request):
    json_request = _get_json(request)
    
    xyquery = JsonXYQuery(JsonTaskModelMap(), json_request)
    json_result = xyquery.do_query()
    
    return _json_response(json_result)



