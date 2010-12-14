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
            # AsyncReply.get() will timeout if the Task was defined with ignore_result=True
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
    
    # Try to get the Task class.  The class is required if we're to record 
    # 'sent' times.
    try:
        taskcls = registry.tasks[taskname]
        send_task = taskcls.apply_async
    except registry.tasks.NotRegistered:
        print 'Unable to retrieve task class.  Using app.send_task method instead.'
        send_task = app_or_default().send_task
        send_task = functools.partial(send_task, taskname)
    
    obj = TaskDemoGroup(uuid=id, completed=False, errors_on_send=0)
    obj.save()
    
    commit_every = 25
    count = 0
    errors_on_send = 0
    results = []
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
            obj.save()
        
        next_dispatch += random.expovariate(rate)
        if next_dispatch > endtime:
            break
        
        while time.time() < next_dispatch:
            # wait for next launch
            pass
    
    ##print 'celerymanagement.demo_dispatch::  finished loop'
    total_time = time.time() - start
    obj.elapsed = total_time
    obj.tasks_sent = count
    obj.save()
    
    ##print 'celerymanagement.demo_dispatch::  saved model'
    # clear results:
    print 'celerymanagement.demo_dispatch::  clearing results (this may take a while).'
    errors_on_result = clear_results(results)
            
    ##print 'celerymanagement.demo_dispatch::  cleared results'
    obj.errors_on_result = errors_on_result
    obj.completed = True
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
    
    # TODO: clear old records?
    
#==============================================================================#
