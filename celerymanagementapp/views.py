import datetime
import calendar
import time
import itertools

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from djcelery.models import WorkerState, TaskState
from celery.registry import TaskRegistry, tasks
from celery.task.control import inspect

from celerymanagementapp.stats import calculate_throughputs, calculate_runtimes

import gviz_api

#==============================================================================#
def test_view(request, taskname=None):
    now = datetime.datetime.now()
    timerange = (now-datetime.timedelta(seconds=120), now)
    start = timerange[0]
    stop = timerange[1]
    states_in_range = TaskState.objects.filter(state='SUCCESS', tstamp__range=(start, stop))
    return HttpResponse(states_in_range)
    
#==============================================================================#
def view_throughputs(request, taskname=None):
    # Simple view, mostly for testing purposes at this point.
    now = datetime.datetime.now()
    timerange = (now-datetime.timedelta(seconds=120), now)
    interval = 15
    throughputs = calculate_throughputs(taskname, timerange, interval)
    return HttpResponse(str(throughputs))

#==============================================================================#
def get_throughput_data(request, taskname=None):
    all_data = [] 
    description = {}
    description['timestamp'] = ("DateTime","timestamp")
    description['tasks'] = ("number","tasks")
    
    now = datetime.datetime.now()
    timerange = (now-datetime.timedelta(seconds=120), now)
    interval = 2
    throughputs = calculate_throughputs(taskname, timerange, interval)
    
    for i, p in enumerate(throughputs):
        data = {}
        data['timestamp'] = now-datetime.timedelta(seconds=120) + datetime.timedelta(seconds=interval*i)
        data['tasks'] = p
        all_data.append(data)

    data_table = gviz_api.DataTable(description)
    data_table.LoadData(all_data)

    if "tqx" in request.GET:
        tqx = request.GET['tqx']
        params = dict([p.split(':') for p in tqx.split(';')])
        reqId = params['reqId'] 
        return HttpResponse(data_table.ToJSonResponse(columns_order=("timestamp","tasks"),req_id=reqId))
    return HttpResponse(data_table.ToJSonResponse(columns_order=("timestamp","tasks")))

def get_runtime_data(request, taskname, search_range=(None,None), runtime_min=0., bin_size=None, bin_count=None):
    runtime_range = (float(runtime_min),None)
    runtimes = calculate_runtimes(taskname, search_range=search_range, runtime_range=runtime_range, bin_size=float(bin_size), bin_count=int(bin_count))
    all_data = []
    description = {}
    description['bin_name'] = ("string","bin_name")
    description['count'] = ("number", "count")

    for (runtime_min, runtime_max), count  in  runtimes:
        data = {}
        data['bin_name'] = str(runtime_min)+" - " + str(runtime_max)
        data['count'] = count
        all_data.append(data)
    
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(all_data)

    if "tqx" in request.GET:        
        tqx = request.GET['tqx']
        params = dict([p.split(':') for p in tqx.split(';')])
        reqId = params['reqId']
        return HttpResponse(data_table.ToJSonResponse(columns_order=("bin_name","count"),      
req_id=reqId))
    return HttpResponse(data_table.ToJSonResponse(columns_order=("bin_name","count")))

def visualize_runtimes(request, taskname, runtime_min=0., bin_count=None, 
                       bin_size=None):
    
    if "submit" in request.POST:
        # Get the search_range:
        search_range_min, search_range_max = None, None
        if 'start_time' in request.POST:
            search_range_min = datetime.datetime.strptime(request.POST['start_time'],"%m/%d/%Y %H:%M:%S")
        if 'end_time' in request.POST:
            search_range_max = datetime.datetime.strptime(request.POST['end_time'],"%m/%d/%Y %H:%M:%S")
        search_range = (search_range_min, search_range_max)
        
        # Get other params:
        runtime_min = float(request.POST.get('runtime_min', runtime_min))
        bin_count = int(request.POST.get('bin_count', bin_count))
        bin_size = float(request.POST.get('bin_size', bin_size))
    else:
        search_range = (None,None)
    
    kwargs = {'taskname': taskname,
              'runtime_min': runtime_min,
              'bin_count': bin_count,
              'bin_size': bin_size,
              }
                
    url = reverse("celerymanagementapp.views.get_runtime_data", kwargs=kwargs)
    return render_to_response('barchart.html',
            {'url':url,'taskname':taskname},
            context_instance=RequestContext(request))

def visualize_throughput(request, taskname=None):
    return render_to_response('timeseries.html',
            {'task': taskname},
            context_instance=RequestContext(request))

def view_defined_tasks(request):
    i = inspect()  
    workers = i.registered_tasks()
    defined = set(x for x in itertools.chain.from_iterable(workers.itervalues()))
    defined = list(defined)
    defined.sort()

    return render_to_response('tasklist.html',
            {'tasks':defined},
            context_instance=RequestContext(request))
            

def view_dispatched_tasks(request, taskname=None):
    """View DispatchedTasks, possibly limited to those for a particular 
       DefinedTask.
    """
    tasks = TaskState.objects.all()
    if taskname:
        tasks = tasks.filter(name=taskname)

    return render_to_response('dispatched_tasklist.html',
            {'tasks': tasks},
            context_instance=RequestContext(request))
    
        

