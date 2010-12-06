import json
import itertools

from django.http import HttpResponse

from celery.task.control import broadcast, inspect
from djcelery.models import WorkerState

from celerymanagementapp.jsonquery.base import JsonFilter
from celerymanagementapp.jsonquery.xyquery import JsonXYQuery
from celerymanagementapp.jsonquery.modelmap import JsonTaskModelMap


#==============================================================================#
def _get_json(request, allow_empty=False):
    """Return the json content of the given request.  The json must be in the 
       request's POST data."""
    rawjson = request.raw_post_data
    if allow_empty and not rawjson:
        return None
    return json.loads(rawjson)
    
def _json_response(jsondata, **kwargs):
    """Convert a Python structure (such as dict, list, string, etc) into a json 
       bystream which is then returned as a Django HttpResponse."""
    rawjson = json.dumps(jsondata, **kwargs)
    return HttpResponse(rawjson, mimetype='application/json')
    
def get_defined_tasks():
    """Get a list of the currently defined tasks."""
    i = inspect()
    workers = i.registered_tasks()
    defined = set(x for x in itertools.chain.from_iterable(workers.itervalues()))
    defined = list(defined)
    defined.sort()
    return defined
    
def get_workers():
    """Get a list of all workers that exist (running or not) in the database."""
    workers = WorkerState.objects.all()
    return [unicode(w) for w in workers]
    

#==============================================================================#
def task_xy_dataview(request):
    json_request = _get_json(request)
    
    xyquery = JsonXYQuery(JsonTaskModelMap(), json_request)
    json_result = xyquery.do_query()
    
    return _json_response(json_result)

def worker_subprocesses_dataview(request):
    """ Return the number of sub processes for each worker as a json 
        dictionary.
    """
    stats = {}
    for x in broadcast("stats", reply=True):
        stats.update(x)
    
    workercounts = {}
    for workername in stats.iterkeys():
        procs = stats[workername]['pool']['processes']
        workercounts[workername] = len(procs)
        
    return _json_response(workercounts)
    
def pending_task_count_dataview(request):
    """ Return the number of pending DispatchedTasks for each defined task.  
        The return value is a json dicitonary with task names as the keys.
    """
    
    json_request = _get_json(request, allow_empty=True) or {}
    tasknames = get_defined_tasks()
    
    filterexp = ['state','PENDING']
    segmentize = {'field': 'taskname', 'method': ['values', tasknames],}
    aggregate = [{'field': 'count'}]
    
    json_request['filter'] = json_request.get('filter',[])
    json_request['filter'].append(filterexp)
    json_request['segmentize'] = segmentize
    json_request['aggregate'] = aggregate
    
    xyquery = JsonXYQuery(JsonTaskModelMap(), json_request)
    json_result = xyquery.do_query()
    
    d = json_result['data']
    r = dict((row[0], row[1]['count']) for row in d)
    
    return _json_response(r)
    
def tasks_per_worker_dataview(request):
    """ Return the number of tasks of each DefinedTask dispatched to each 
        worker.  The return value is a two-level json dictionary where the 
        top-level keys are the task names and the second-level keys are the 
        worker names.
    
        For example:
        
            {
                task1: {
                    worker1: 0,
                    worker2: 5
                }
                task2: {
                    worker1: 18,
                    worker2: 9
                }
            }
        
    """
    
    json_request = _get_json(request, allow_empty=True) or {}
    
    modelmap = JsonTaskModelMap()
    jfilter = JsonFilter(modelmap, json_request)
    queryset = modelmap.get_queryset()
    queryset = jfilter(queryset)
    
    tasknames = get_defined_tasks()
    workers = [(unicode(obj), obj.pk) for obj in WorkerState.objects.all()]
    
    r = {}
    
    for wname, wpk in workers:
        worker_queryset = queryset.filter(worker=wpk)
        for taskname in tasknames:
            n = worker_queryset.filter(name=taskname).count()
            if taskname not in r:
                r[taskname] = {}
            r[taskname][wname] = n
    return _json_response(r)

#==============================================================================#

