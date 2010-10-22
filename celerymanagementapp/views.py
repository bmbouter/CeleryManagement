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

import gviz_api

#==============================================================================#
class Throughput(object):
    """Calculate the throughput for a DefinedTask over a specified period of 
       time.
    """
    units = { 'MICROSEC':0.001, 'SECOND':1, 'MINUTE':60, 'HOUR':3600, 
              'DAY':86400, 
            }
    
    def __init__(self, taskname, mintime, maxtime):
        """mintime and maxtime must be datetime.datetime or datetime.date 
           objects.
        """
        self.taskname = taskname
        self.mintime = mintime
        self.maxtime = maxtime
        qs = TaskState.objects.filter(name=taskname, state='SUCCESS', 
                                      tstamp__range=(mintime, maxtime))
        self.count = qs.count()
        diff = maxtime-mintime  # assumed to be a datetime.timedelta object
        self.secs = diff.days*86400 + diff.seconds + diff.microseconds*0.001
        
    def __call__(self, unit):
        """Calculate the throughput.  ``unit`` can be a known unit (as defined 
           in units) or a number of seconds to use as the unit.
        """
        if isinstance(unit, basestring):
            unit = self.units[unit]
        if self.secs == 0:
            return 0
        return self.count*unit / self.secs
        
        
def calculate_throughputs(taskname, timerange, interval=1):
    """ Calculates the throughputs for a given task for each interval over the 
        given timerange.
        
        timerange = Range over which to calculate throughputs.  Must be a tuple 
                    of two datetime.datetime or datetime.date objects.
        interval = How often (in seconds) to calculate throughputs.
        
        Returns a list of throughputs.  Each throughput is calculated over the 
        given interval.  The throughputs collectively span the given time 
        range.
    """
    start = timerange[0]
    stop = timerange[1]
    if taskname:
        states_in_range = TaskState.objects.filter(name=taskname, state='SUCCESS', 
                                                   tstamp__range=(start, stop))
    else:
        states_in_range = TaskState.objects.filter(state='SUCCESS', 
                                                   tstamp__range=(start, stop))
    
    # TODO: clean up the following code
    throughputs = []
    finterval = float(interval)
    interval_secs = datetime.timedelta(seconds=interval)
    mintime = start
    while mintime < stop:
        maxtime = mintime + interval_secs
        qs = states_in_range.filter(tstamp__range=(mintime, maxtime))
        throughputs.append(qs.count()/finterval)
        mintime = maxtime
    
    return throughputs
    
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
    interval = 15
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

