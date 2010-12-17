import time
import datetime
import random
import functools
import traceback

from celery import registry
from celery.app import app_or_default
from celery.exceptions import TimeoutError

from celerymanagementapp.models import TaskDemoGroup

#==============================================================================#
DELETE_TASKDEMOGROUPS_AFTER = 1  # days

def clear_results(results):
    """ Clear the results from the given iterable. Returns the number of 
        exceptions found.
    """
    ##print 'clearing results...'
    ##print 'results length: {0}'.format(len(results))
    errors = 0
    for r in results:
        ##print 'clearing result.'
        try:
            r.get(timeout=1.0)
        except TimeoutError:
            # AsyncReply.get() will timeout if the Task was defined with 
            # ignore_result=True
            pass
        except Exception:
            errors += 1
    return errors

def demo_dispatch(taskname, id, runfor, rate, options=None, args=None, kwargs=None):
    print 'celerymanagement.demo_dispatch::  task: {0}'.format(taskname)
    ##print ' ::  options: {0}'.format(options)
    ##print ' ::  args:    {0}'.format(args)
    ##print ' ::  kwargs:  {0}'.format(kwargs)
    
    options = options or {}
    args = args or []
    kwargs = kwargs or {}
    
    # Do not ignore results unless we are sure the task does not produce any.
    task_ignores_results = False
    
    # Try to get the Task class.  The class is required if we're to record 
    # 'sent' times.
    try:
        taskcls = registry.tasks[taskname]
        send_task = taskcls.apply_async
        task_ignores_results = taskcls.ignore_result
    except registry.tasks.NotRegistered:
        print 'Unable to retrieve task class.  Using app.send_task method instead.'
        send_task = app_or_default().send_task
        send_task = functools.partial(send_task, taskname)
    
    obj = TaskDemoGroup(uuid=id, name=taskname, completed=False, 
                        errors_on_send=0, timestamp=datetime.datetime.now(),
                        requested_rate=rate, requested_runfor=runfor)
    obj.save()
    
    commit_every = 25
    count = 0
    errors_on_send = 0
    errors_on_result = 0
    results = []
    sleep_fudge_factor = 0.1
    #publisher = 
    ##lambd = 1./rate
    start = time.time()  # minimize the code between this and the loop below
    endtime = start + runfor
    next_dispatch = start
    
    ##print 'time:    {0}'.format(time.time())
    ##print 'endtime: {0}'.format(endtime)
    
    # the loop...
    while time.time() < endtime:
        
        try:
            r = send_task(args=args, kwargs=kwargs, **options)
            print 'Task state: {0}'.format(r.state)
            if r.failed():
                errors_on_send += 1
            results.append(r)
            count += 1
        except:
            print 'Caught exception while trying to send task.'
            traceback.print_exc()
            errors_on_send += 1
            obj.errors_on_send = errors_on_send
            obj.save()
            break
        
        if (count % commit_every) == 0:
            obj.elapsed = time.time()-start
            obj.tasks_sent = count
            obj.errors_on_send = errors_on_send
            obj.save()
        
        next_dispatch += random.expovariate(rate)
        next_dispatch = min(endtime, next_dispatch)
        
        sleep_time = next_dispatch - (time.time()+sleep_fudge_factor)
        if sleep_time > 0.:
            time.sleep(sleep_time)
        
        while time.time() < next_dispatch:
            # wait for next launch
            pass
    
    ##print 'celerymanagement.demo_dispatch::  finished loop'
    total_time = time.time() - start
    obj.elapsed = total_time
    obj.tasks_sent = count
    obj.errors_on_send = errors_on_send
    obj.timestamp = datetime.datetime.now()
    obj.save()
    
    ##print 'celerymanagement.demo_dispatch::  saved model'
    # We must clear the results.  If a task produces results, those results 
    # stick around in the system until they're read.
    if not task_ignores_results:
        msg = 'celerymanagement.demo_dispatch::  '
        msg += 'clearing results (this may take a while).'
        print msg
        errors_on_result = clear_results(results)
            
    ##print 'celerymanagement.demo_dispatch::  cleared results'
    obj.errors_on_result = errors_on_result
    obj.completed = True
    obj.timestamp = datetime.datetime.now()
    obj.save()
    
    print 'celerymanagement.demo_dispatch:: results:'
    print '  name:              {0}'.format(taskname)
    print '  runfor:            {0}'.format(runfor)
    print '  desired rate:      {0}'.format(rate)
    print '  count:             {0}'.format(count)
    print '  total_time:        {0}'.format(total_time)
    print '  actual rate:       {0}'.format(count/total_time)
    print '  errors_on_result:  {0}'.format(errors_on_result)
    print '  errors_on_send:    {0}'.format(errors_on_send)
    
    # clear old records
    keepdays = datetime.timedelta(days=DELETE_TASKDEMOGROUPS_AFTER)
    maxdate = datetime.datetime.now() - keepdays
    TaskDemoGroup.objects.filter(timestamp__lt=maxdate).delete()
    
#==============================================================================#
