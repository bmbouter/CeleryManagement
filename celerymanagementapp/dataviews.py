import json
import itertools

from django.http import HttpResponse

from celery.task.control import broadcast, inspect
from djcelery.models import WorkerState

from celerymanagementapp.jsonquery.base import JsonFilter
from celerymanagementapp.jsonquery.xyquery import JsonXYQuery
from celerymanagementapp.jsonquery.modelmap import JsonTaskModelMap


#==============================================================================#
def _json_from_post(request, allow_empty=False):
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
    return HttpResponse(rawjson, content_type='application/json')
    
def _update_json_request(json_request, **kwargs):
    if 'filter' in kwargs:
        filter = json_request.get('filter',[])
        filter.extend(kwargs.pop('filter'))
        json_request['filter'] = filter
    if 'exclude' in kwargs:
        exclude = json_request.get('exclude',[])
        exclude.extend(kwargs.pop('exclude'))
        json_request['exclude'] = exclude
    json_request.update(dict((k,v) for k,v in kwargs.iteritems() if v is not None))
    return json_request
        
    
def _resolve_name(name):
    """If name is None or 'all', return None.  Otherwise, returns name."""
    if not name or name.lower() == 'all':
        name = None
    return name
        
    
def _get_tasknames_from_database():
    qs = JsonTaskModelMap().get_queryset()
    return qs.values_list('name', flat=True).distinct().order_by()
    
def get_defined_tasks():
    """Get a list of the currently defined tasks."""
    global _taskname_cache
    i = inspect()
    workers = i.registered_tasks()
    #defined = []
    if workers:
        defined = set(x for x in itertools.chain.from_iterable(workers.itervalues()))
        defined = list(defined)
        defined.sort()
        _taskname_cache = defined
    return _taskname_cache
    
def get_workers_from_database():
    """Get a list of all workers that exist (running or not) in the database."""
    workers = WorkerState.objects.all()
    return [unicode(w) for w in workers]
    
def get_workers_live():
    i = inspect()
    workers = i.ping()
    workers = list(workers.iterkeys())  if workers else  []
    return workers
    

#==============================================================================#
def task_xy_dataview(request):
    json_request = _json_from_post(request)
    
    xyquery = JsonXYQuery(JsonTaskModelMap(), json_request)
    json_result = xyquery.do_query()
    
    return _json_response(json_result)

def worker_subprocesses_dataview(request, name=None):
    """ Return the number of sub processes for each worker as a json 
        dictionary.
    """
    name = _resolve_name(name)
    stats = {}
    dest = name and [name]
    for x in broadcast("stats", destination=dest, reply=True):
        stats.update(x)
    
    workercounts = {}
    for workername in stats.iterkeys():
        procs = stats[workername]['pool']['processes']
        workercounts[workername] = len(procs)
        
    return _json_response(workercounts)
    
def pending_task_count_dataview(request, name=None):
    """ Return the number of pending DispatchedTasks for each defined task.  
        The return value is a json dicitonary with task names as the keys.
    """
    name = _resolve_name(name)
    json_request = _json_from_post(request, allow_empty=True) or {}
    tasknames = get_defined_tasks()
    
    filterexp = [['state','PENDING']]
    if name:
        filterexp.append(['name',name])
    segmentize = {'field': 'taskname', 'method': ['values', tasknames],}
    aggregate = [{'field': 'count'}]
    
    json_request = _update_json_request(json_request, filter=filterexp, 
                                        segmentize=segmentize, 
                                        aggregate=aggregate)
    
    xyquery = JsonXYQuery(JsonTaskModelMap(), json_request)
    json_result = xyquery.do_query()
    
    d = json_result['data']
    r = dict((row[0], row[1]['count']) for row in d)
    
    return _json_response(r)
    
def tasks_per_worker_dataview(request, name=None):
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
    name = _resolve_name(name)
    json_request = _json_from_post(request, allow_empty=True) or {}
    
    filterexp = []
    if name:
        filterexp.append(['name',name])
    json_request = _update_json_request(json_request, filter=filterexp)
    
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
    
def definedtask_list_dataview(request):
    tasknames = get_defined_tasks()
    return _json_response(tasknames)
    
def worker_list_dataview(request):
    workernames = get_workers_live()
    return _json_response(workernames)
    
def worker_info_dataview(request, name=None):
    name = _resolve_name(name)
    if name:
        workers = WorkerState.objects.all(hostname=name)
    else:
        workers = WorkerState.objects.all()
    d = dict((unicode(w), {'is_alive': w.is_alive()}) for w in workers)
    return _json_response(d)

#==============================================================================#

