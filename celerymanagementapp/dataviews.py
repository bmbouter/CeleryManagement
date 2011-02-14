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
import traceback

from django.http import HttpResponse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse as urlreverse
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.html import urlquote

from celery import signals
from celery.task.control import broadcast, inspect
from djcelery.models import WorkerState

from celerymanagementapp import timeutil

from celerymanagementapp.jsonquery.filter import JsonFilter
from celerymanagementapp.jsonquery.xyquery import JsonXYQuery
from celerymanagementapp.jsonquery.modelmap import JsonTaskModelMap
from celerymanagementapp.policy import create_policy, save_policy
from celerymanagementapp.policy import exceptions as policy_exceptions

from celerymanagementapp import tasks, jsonutil
from celerymanagementapp.models import OutOfBandWorkerNode, RegisteredTaskType
from celerymanagementapp.models import TaskDemoGroup, Provider, InBandWorkerNode
from celerymanagementapp.models import PolicyModel
from celerymanagementapp.forms import OutOfBandWorkerNodeForm, ProviderForm
from celerymanagementapp.forms import PolicyModelForm

#==============================================================================#
# Utility functions/classes
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
# task/worker dataviews
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
    
    ##import pprint
    ##pprint.pprint(json_result)
    
    ##print jsonutil.dumps(json_result)
    
    return _json_response(json_result)
    
def task_xy_metadata(request):
    """ Retrieve metadata about the task_xy_dataview fields. """
    meta = JsonTaskModelMap().get_metadata()
    return _json_response(meta)

def worker_subprocesses_dataview(request, name=None):
    """ Return the number of sub processes for each worker as a json 
        dictionary.
    """
    name = _resolve_name(name)
    dest = name and [name]
    workercounts = get_worker_subprocesses(dest=dest)
        
    return _json_response(workercounts)

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
# Provider dataviews.
def create_provider(request):
    """Create a Provider"""
    if request.method == 'POST':
        new_obj = ProviderForm(request.POST, request.FILES)
        if new_obj.is_valid():
            new_obj.save()
            providers = Provider.objects.all()
            return render_to_response('celerymanagementapp/configure.html',
                {'provider_form': new_obj,
                "providers" : providers,
                "load_test_data" : "true" },
                context_instance=RequestContext(request))
        else:
            providers = Provider.objects.all()
            return render_to_response('celerymanagementapp/configure.html',
                {'provider_form': new_obj,
                "providers" : providers,
                "load_test_data" : "true" },
                context_instance=RequestContext(request))

def provider_images(request):
    """Returns a list of images for a Provider"""
    p = Provider(provider_user_id=request.POST['provider_user_id'],
            provider_key=request.POST['provider_key'],
            provider_name=request.POST['provider_name'])
    if not p.are_credentials_valid():
        failed = { 'failure' : 'Invalid Provider Credentials'}
        json = simplejson.dumps(failed)
        return HttpResponse(json)
    images = p.conn.list_images()
    json_images = []
    [json_images.append({'name': item.name, 'id': item.id}) for item in images]
    json = simplejson.dumps(json_images)
    return HttpResponse(json)

#==============================================================================#
# out-of-band/in-band worker dataviews.
def delete_inbandworker(request, worker_pk):
    """Deletes an InBandWorkerNode object"""
    try:
        worker = InBandWorkerNode.objects.get(pk=worker_pk)
        worker.delete()
    except Exception as e:
        failed = { 'failure' : e.args[0]}
        json = simplejson.dumps(failed)
        return HttpResponse(json)

def delete_provider(request, provider_pk):
    """Deletes a provider object and all corresponding InBandWorkerNode objects"""
    for inbandworker in InBandWorkerNode.objects.filter(provider=provider_pk):
        inbandworker.delete()
    Provider.objects.get(pk=provider_pk).delete()

def delete_outofbandworker(request, worker_pk):
    """Deletes an OutOfBandWorkerNode"""
    try:
        worker = OutOfBandWorkerNode.objects.get(pk=worker_pk)
        worker.delete()
    except Exception as e:
        failed = { 'failure' : e.args[0]}
        json = simplejson.dumps(failed)
        return HttpResponse(json)

def create_or_update_outofbandworker(request, worker_pk=None):
    """Create an OutOfBandWorker"""
    if request.method == 'POST':
        if worker_pk is None:
            new_obj = OutOfBandWorkerNodeForm(request.POST, request.FILES)
        else:
            worker_node = OutOfBandWorkerNode.objects.get(pk=worker_pk)
            new_obj = OutOfBandWorkerNodeForm(request.POST, request.FILES, instance=worker_node)
        if new_obj.is_valid():
            worker = new_obj.save()
            if worker_pk is not None:
                json = simplejson.dumps("Worker successfully updated.")
            else:
                context = { 'worker': {'worker': worker,
                            'workerForm': new_obj }}
                html = render_to_response("celerymanagementapp/configure_outofbandworker_instance.html",
                        context,
                        context_instance=RequestContext(request))
                success = { 'success': 'Worker successfully created.',
                            'html': urlquote(html.content),
                            'pk': worker.pk }
                json = simplejson.dumps(success)
        else:
            errors = []
            for field in new_obj:
                errors.append({ 'field' : field.html_name,
                                'error' : field.errors })
            failed = { 'failure' : errors,
                        'id': worker_pk }
            json = simplejson.dumps(failed)
        return HttpResponse("<textarea>" + json + "</textarea>")

def worker_start(request):
    """Find an available node and start a worker process"""
    active_nodes = OutOfBandWorkerNode.objects.filter(active=True)
    for node in active_nodes:
        if not node.is_celeryd_running():
            node.celeryd_start()
            return _json_response({'status': 'success'})
    return _json_response({'status': 'failure', 'message': 'No Available Worker Nodes'})
    
#==============================================================================#
# Policy dataviews
class PolicyDataviewError(Exception):
    """ Raised to immediately stop the processing of a Policy-related dataview.  
        This exception is caught in PolicyDataviewBase.__call__. 
    """
    pass
    
class PolicyDataviewBase(object):
    """ Base class for handling Policy-related dataviews.  This is meant to be 
        subclassed.  The behavior specific to particular dataviews is defined 
        in those subclasses.
    """
    def __init__(self):
        self.success = False
        self.record = {'id': -1, 'name': '', 'source': '', 'enabled': False, 
                       'modified': None, 'last_run_time': None,}
        self.error_info = {'compile_error': False, 'type': '', 'msg': '', 
                           'traceback': ''}
    def _result(self):
        return (self.success, self.record, self.error_info)
        
    def _error(self, **kwargs):
        """ Sets items in the error_info attribute, then raises a 
            PolicyDataviewError exception.  This exception is caught in the 
            __call__ method. 
        """
        for k,v in kwargs.iteritems():
            assert k in self.error_info
            self.error_info[k] = v
        raise PolicyDataviewError()
        
    def __call__(self, *args, **kwargs):
        """ Process a dataview request.  Specific behavior is delegated to 
            subclasses. 
        """
        # If an error occurs while processing the request, an exception is 
        # raised which causes the processing to halt immediately.  The 
        # exception is caught here.
        try:
            self.do_dataview(*args, **kwargs)
        except PolicyDataviewError:
            pass
        return self._result()
        
    def do_dataview(self, *args, **kwargs):
        raise NotImplementedError
        
    def parse_json_request(self, json_request, names):
        # Used by derived classes.
        try:
            for name in names:
                setattr(self, name, json_request[name])
        except KeyError:
            names = ', '.join('"{0}"'.format(s) for s in names)
            s = 'Bad request data.  Expected the keys: {0}.'.format(names)
            self._error(msg=s, type='KeyError')
        
    def get_model(self, id):
        # Used by derived classes.
        try:
            m = PolicyModel.objects.get(id=id)
        except ObjectDoesNotExist:
            s = 'There is no policy with the given id: {0}.'.format(id)
            self._error(msg=s, type='ObjectDoesNotExist')
        return m
        
    def verify_name_is_unique(self, name, id=None):
        # Used by derived classes.
        objs = PolicyModel.objects.filter(name=name)
        if id is None:
            if objs.exists():
                s = 'A policy with the name {0} already exists.'.format(name)
                self._error(msg=s, type='DuplicateName')
            else:
                return True
        else:
            if objs.exists() and objs[0].id != id:
                s = 'A different policy with the name "{0}" already exists.'.format(name)
                self._error(msg=s, type='DuplicateName')
            else:
                return True
            
    def make_record(self, model):
        # Used by derived classes.
        return {
            'id': model.id,
            'name': model.name,
            'source': model.source,
            'enabled': model.enabled,
            'modified': model.modified and timeutil.datetime_from_python(model.modified),
            'last_run_time': model.last_run_time and timeutil.datetime_from_python(model.last_run_time),
            }
            
    def create_policy(self):
        """ Creates the policy model.  If the source cannot be compiled, this will fail. """
        # Used by derived classes.
        try:
            m = create_policy(self.name, source=self.source, enabled=self.enabled)
            self.record = self.make_record(m)
            self.success = True
        except policy_exceptions.Error as e:
            self._error(compile_error=True, msg=e.formatted_message, 
                        type=str(type(e)), traceback='')
        except Exception as e:
            self._error(compile_error=True, msg=e.msg, type=str(type(e)), 
                        traceback=traceback.format_exc())
        return True
        
    def save_policy(self, model):
        """ Modifies the policy model.  If the source cannot be compiled, this will fail. """
        # Used by derived classes.
        try:
            model.name = self.name
            model.source = self.source
            model.enabled = self.enabled
            save_policy(model)  # This throws if it cannot save.
            self.record = self.make_record(model)
            self.success = True
        except policy_exceptions.Error as e:
            self._error(compile_error=True, msg=e.formatted_message, 
                        type=str(type(e)), traceback='')
        except Exception as e:
            self._error(compile_error=True, msg=e.msg, type=str(type(e)), 
                        traceback=traceback.format_exc())
        return True
        
    def delete_policy(self, model):
        # Used by derived classes.
        self.record = self.make_record(model)
        model.delete()
        self.success = True
        return True
        
    def get_policy(self, model):
        # Used by derived classes.
        self.record = self.make_record(model)
        self.success = True
        return True
    
        
class PolicyCreate(PolicyDataviewBase):
    def __init__(self):
        super(PolicyCreate, self).__init__()
    def do_dataview(self, json_request):
        self.parse_json_request(json_request, ('name','source','enabled'))
        self.verify_name_is_unique(self.name)
        self.create_policy()
        
class PolicyModify(PolicyDataviewBase):
    def __init__(self):
        super(PolicyModify, self).__init__()
    def do_dataview(self, json_request, id):
        self.parse_json_request(json_request, ('name','source','enabled'))
        model = self.get_model(id)
        self.verify_name_is_unique(self.name, id)
        self.save_policy(model)
        
class PolicyDelete(PolicyDataviewBase):
    def __init__(self):
        super(PolicyDelete, self).__init__()
    def do_dataview(self, id):
        model = self.get_model(id)
        self.delete_policy(model)
        
class PolicyGet(PolicyDataviewBase):
    def __init__(self):
        super(PolicyGet, self).__init__()
    def do_dataview(self, id):
        model = self.get_model(id)
        self.get_policy(model)
        

def policy_create(request):
    if request.method == "POST":
        policy_form = PolicyModelForm(request.POST)
        if policy_form.is_valid():
            policy = policy_form.save()
            context = { 'policy': {'policy': policy,
                        'policyForm': policy_form }}
            html = render_to_response("celerymanagementapp/policy_instance.html",
                    context,
                    context_instance=RequestContext(request))
            success = { 'success': 'Policy successfully created.',
                        'html': html.content,
                        'pk': policy.pk }
            json = simplejson.dumps(success)
        else:
            errors = []
            for field in policy_form:
                errors.append({ 'field' : field.html_name,
                                'error' : field.errors })
            failed = { 'failure' : errors }
            json = simplejson.dumps(failed)
        return HttpResponse(json)
    
def policy_modify(request, policy_id=None):
    if request.method == "POST":
        try:
            policy = PolicyModel.objects.get(pk=policy_id)
        except ObjectDoesNotExist:
            m = 'No Policy with the given ID ({0}) was found.'.format(policy_id)
            failed = { 'failure' : m,
                        'id': policy_id }
            json = simplejson.dumps(failed)
        else:
            policy_form = PolicyModelForm(request.POST, instance=policy)
            if policy_form.is_valid():
                policy_form.save()
                json = simplejson.dumps("Policy successfully updated.")
            else:
                errors = []
                for field in policy_form:
                    errors.append({ 'field' : field.html_name,
                                    'error' : field.errors })
                failed = { 'failure' : errors,
                            'id': policy_id }
                json = simplejson.dumps(failed)
        return HttpResponse(json)
    
def policy_delete(request, policy_id=None):
    """Deletes a Policy"""
    try:
        policy = PolicyModel.objects.get(pk=policy_id)
        policy.delete()
        json = simplejson.dumps("Policy successfully deleted.")
    except Exception as e:
        failed = { 'failure' : e.args[0]}
        json = simplejson.dumps(failed)
    return HttpResponse(json)
    
def policy_get(request, id):
    getter = PolicyGet()
    success, record, error_info = getter(id)
        
    json_result = {'success':       success, 
                   'record':        record, 
                   'error_info':    error_info}
    
    return _json_response(json_result)
    
def policy_list(request):
    def make_row(obj):
        return {
            'id': obj.id, 
            'name': obj.name, 
            'enabled': obj.enabled, 
            'modified': obj.modified and timeutil.datetime_from_python(obj.modified), 
            'last_run_time': obj.last_run_time and timeutil.datetime_from_python(obj.last_run_time),
            }
    qs = PolicyModel.objects.all()
    ret = [make_row(obj) for obj in qs]
    return _json_response(ret)
    

#==============================================================================#
# task-demo dataviews
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
            rawjson = request.raw_post_data
            ##print 'Launching dispatcher task...'
            r = tasks.launch_demotasks.apply_async(args=[rawjson])
            dispatchid = uuid.UUID(r.task_id).hex
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

