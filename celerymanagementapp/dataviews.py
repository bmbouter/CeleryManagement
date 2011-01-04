"""
    Django view functions that return Json data.
"""

#import json
import itertools
import socket
import uuid
import tempfile
import os
import subprocess
import time

from django.http import HttpResponse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse as urlreverse
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.template import RequestContext

from celery import signals
from celery.task.control import broadcast, inspect
from djcelery.models import WorkerState

from celerymanagementapp.jsonquery.filter import JsonFilter
from celerymanagementapp.jsonquery.xyquery import JsonXYQuery
from celerymanagementapp.jsonquery.modelmap import JsonTaskModelMap

from celerymanagementapp import tasks, jsonutil
from celerymanagementapp.models import OutOfBandWorkerNode, RegisteredTaskType
from celerymanagementapp.models import TaskDemoGroup
from celerymanagementapp.forms import OutOfBandWorkerNodeForm

#==============================================================================#
def _json_from_post(request, *args, **kwargs):
    """Return the json content of the given request.  The json must be in the 
       request's POST data."""
    rawjson = request.raw_post_data
    if kwargs.pop('allow_empty',False) and not rawjson:
        return None
    return jsonutil.loads(rawjson, *args, **kwargs)
    
def _json_response(jsondata, *args, **kwargs):
    """Convert a Python structure (such as dict, list, string, etc) into a json 
       bystream which is then returned as a Django HttpResponse."""
    rawjson = jsonutil.dumps(jsondata, *args, **kwargs)
    return HttpResponse(rawjson, content_type='application/json')
    
def _update_json_request(json_request, **kwargs):
    """ Merges the keyword arguments with the contents on the json_request 
        dict.  
        
        If 'filter' or 'exclude' are given (whose values should be a list of 
        lists), their values are appended to the values of the same name in the 
        json dict.  Other arguments replace the corresponding values in the 
        dict.
    """
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
    
    
class SimpleCache(object):
    def __init__(self, refresh_interval=20.0):
        self._cache = []
        self._next_refresh = 0.0  # timestamp in seconds, as returned from time.time()
        self._refresh_interval = refresh_interval  # seconds
        
    def getdata(self):
        if self._next_refresh < time.time():
            self._next_refresh = time.time() + self._refresh_interval
            self._cache = self.refresh()
        return self._cache
        
    data = property(getdata)
    
    def refresh(self):
        raise NotImplementedError()
        
class TaskListCache(SimpleCache):
    def refresh(self):
        qs = RegisteredTaskType.objects.all()
        names = list(set(obj.name for obj in qs))
        names.sort()
        return names
        
class WorkerStateCache(SimpleCache):
    def refresh(self):
        return [w for w in WorkerState.objects.all()]
        
_worker_state_cache = WorkerStateCache()
_task_list_cache = TaskListCache()

    
def get_defined_tasks():
    """Get a list of the currently defined tasks."""
    return _task_list_cache.data
    
def get_defined_tasks_live():
    """ Get the list of defined tasks as reported by Celery right now. """
    i = inspect()
    workers = i.registered_tasks()
    defined = []
    if workers:
        defined = set(x for x in itertools.chain.from_iterable(workers.itervalues()))
        defined = list(defined)
        defined.sort()
    return defined
    
def get_workers_from_database():
    """Get a list of all workers that exist (running or not) in the database."""
    return [unicode(w) for w in _worker_state_cache.data]
    
def get_workers_live():
    """ Get the list of workers as reported by Celery right now. """
    i = inspect()
    workersdict = i.ping()
    workers = []
    if workersdict:
        workers = set(workersdict.iterkeys())
        workers.add(socket.gethostname())
        workers = list(workers)
        workers.sort()
    return workers
    
def get_worker_subprocesses(dest=None):
    """ Retrieve the number of subprocesses for each worker.  The return value 
        is a dict where the keys are worker names and the values are the number 
        of subprocesses. 
    """
    stats = {}
    for x in broadcast("stats", destination=dest, reply=True):
        stats.update(x)
    
    workercounts = {}
    for workername in stats.iterkeys():
        procs = stats[workername]['pool']['processes']
        workercounts[workername] = len(procs)
    
    return workercounts
    

#==============================================================================#
def task_xy_dataview(request):
    """ Performs a database query and returns the results of that query.  The 
        result is formatted as json.  The query must be contained in the 
        request's POST content and it must be fin json format.  
        
        See the docs directory form more information on the format of the query 
        and result.
    """
    json_request = _json_from_post(request)
    
    xyquery = JsonXYQuery(JsonTaskModelMap(), json_request)
    json_result = xyquery.do_query()
    
    return _json_response(json_result)

def worker_subprocesses_dataview(request, name=None):
    """ Return the number of sub processes for each worker as a json 
        dictionary.
    """
    name = _resolve_name(name)
    dest = name and [name]
    workercounts = get_worker_subprocesses(dest=dest)
        
    return _json_response(workercounts)

def create_outofbandworker(request):
    """Create an OutOfBandWorker"""
    if request.method == 'POST':
        new_obj = OutOfBandWorkerNodeForm(request.POST, request.FILES)
        if new_obj.is_valid():
            new_obj.save()
            OutOfBandWorkers = OutOfBandWorkerNode.objects.all()
            return HttpResponse("success")
        else:
            errors = []
            for field in new_obj:
                errors.append({ 'field' : field.html_name,
                                'error' : field.errors })
            failed = { 'failure' : errors }
            json = simplejson.dumps(failed)
            return HttpResponse("<textarea>" + json + "</textarea>")


def worker_start(request):
    """Find an available node and start a worker process"""
    active_nodes = OutOfBandWorkerNode.objects.filter(active=True)
    for node in active_nodes:
        output = node.celeryd_status()
        if not output.strip('\n').isdigit():
            node.celeryd_start()
            return _json_response({'status': 'success'})
    return _json_response({'status': 'failure', 'message': 'No Available Worker Nodes'})
    
def pending_task_count_dataview(request, name=None):
    """ Return the number of pending DispatchedTasks for each defined task.  An 
        optional filter and/or exclude may be provided in the POST data as a 
        json query.  The return value is a json dicitonary with task names as 
        the keys.
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
    
    #r = dict((row[0], row[1]['count']) for row in d)
    r = dict((row[0], row[1][0]['methods'][0]['value']) for row in d)
    
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
            
        An optional filter and/or exclude may be provided in the POST data as a 
        json query.  
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
    workers = [(unicode(obj), obj.pk) for obj in _worker_state_cache.data]
    
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
    """ Returns a list of DefinedTasks names, formatted as json. """
    tasknames = get_defined_tasks()
    return _json_response(tasknames)
    
def worker_list_dataview(request):
    """ Returns a list of worker names, formatted as json. """
    workernames = get_workers_live()
    return _json_response(workernames)
    

#==============================================================================#
TASKDEMO_RUNFOR_MAX = 60.*10  # ten minutes

def validate_task_demo_request(json_request):
    """ Helper to task_demo_dataview.  It validates the Json request. """
    # return (is_valid, msg)
    name = json_request.get('name', None)
    rate = json_request.get('rate', None)
    runfor = json_request.get('runfor', None)
    if not name or not rate or not runfor:
        return False, "The keys: 'name', 'rate', and 'runfor' are all required."
    if not isinstance(rate, (int,float)) or not isinstance(runfor, (int,float)):
        return False, "The keys: 'rate' and 'runfor' must be integers or floats."
    
    kwargs = json_request.get('kwargs', {})
    args = json_request.get('args', [])
    options = json_request.get('options', {})
    
    if not isinstance(kwargs, dict):
        return False, "The key: 'kwargs', if present, must be a dictionary."
    if not isinstance(args, list):
        return False, "The key: 'args', if present, must be a list."
    if not isinstance(options, dict):
        return False, "The key: 'options', if present, must be a dictionary."
    
    defined = get_defined_tasks_live()
    if name not in defined:
        return False, "There is no task by the name: '{0}'.".format(name)
    if runfor > TASKDEMO_RUNFOR_MAX:
        msg =  'The task runfor value, {0}, exceeds the '.format(runfor)
        msg += 'maximum allowable value of {0}.'.format(TASKDEMO_RUNFOR_MAX)
        return False, msg
    
    return True, ""
    

def task_demo_dataview(request):
    """ View that launches a single task several times.  This can be used to 
        stress test a particular Celery configuration. 
    
        The request must include the Json request as POST data.
    """
    if request.method != 'POST':
        response = {
            'uuid': None,
            'error': True,
            'msg': "Http Request must use the POST method.",
            }
        return _json_response(response)
    else:
        json_request = _json_from_post(request)
        
        dispatchid = None
        
        # validate request
        is_valid, msg = validate_task_demo_request(json_request)
        if is_valid:
            # save json to temp file
            rawjson = request.raw_post_data
            fd, tmpname = tempfile.mkstemp()
            os.close(fd)
            tmp = open(tmpname, 'wb')
            tmp.write(rawjson)
            tmp.close()
            # generate id
            dispatchid = uuid.uuid4().hex
            ##print 'Launching dispatcher task...'
            tasks.launch_demotasks.apply_async(args=[dispatchid, tmpname])
            ##print 'Dispatcher task launched.'
            
        # prepare response
        response = {
            'uuid': dispatchid,
            'error': not is_valid,
            'msg': msg,
            }
        
        return _json_response(response)
    
def task_demo_status_dataview(request, uuid=None):
    """ Retrieve the status of the task demo with the given uuid.  The status 
        is returned as Json data. 
    """
    # default values
    response = {
        'name': '<invalid>',
        'status': 'NOTFOUND',
        'completed': False,
        'elapsed': -1.0,
        'tasks_sent': -1,
        'errors_on_send': -1,
        'errors_on_result': -1,
        'orig_request': {}
        }
    try:
        # get object from db
        obj = TaskDemoGroup.objects.get(uuid=uuid)
        orig_request = {
            'rate': obj.requested_rate,
            'runfor': obj.requested_runfor,
            }
        response = {
            'name': obj.name,
            'completed': obj.completed,
            'elapsed': obj.elapsed,
            'tasks_sent': obj.tasks_sent,
            'errors_on_send': obj.errors_on_send,
            'errors_on_result': obj.errors_on_result,
            'orig_request': orig_request,
            }
        status = 'RUNNING'
        if obj.completed:
            if obj.errors_on_send or obj.errors_on_result:
                status = 'ERROR'
            else:
                status = 'SUCCESS'
        response['status'] = status
    except ObjectDoesNotExist:
        pass
    return _json_response(response)



#==============================================================================#

