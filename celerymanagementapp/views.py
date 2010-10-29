import datetime
import calendar
import time

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

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

def visualize_throughput(request, taskname=None):
    return render_to_response('timeseries.html',
            {'task': taskname},
            context_instance=RequestContext(request))

