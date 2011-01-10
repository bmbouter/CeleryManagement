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
TASKDEMO_COMMIT_EVERY = 25

def clear_results(results):
    """ Clear the results from the given iterable. Returns the number of 
        exceptions found.
    """
    errors = 0
    for r in results:
        try:
            r.get(timeout=1.0)
        except TimeoutError:
            # AsyncReply.get() will timeout if the Task was defined with 
            # ignore_result=True
            pass
        except Exception:
            errors += 1
    return errors
    
        
        
class ApplyAsyncWrapper(object):
    def __init__(self, taskname, options, args, kwargs):
        self.taskname = taskname
        # Do not ignore results unless we're sure the task doesn't produce any.
        self.ignores_results = False
        self.options = options or {}
        self.args = args or []
        self.kwargs = kwargs or {}
        self.send_task = None
        self.publisher = None
        self._init_sendtask(taskname)
        
    def __enter__(self):
        # create connection
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        # close connection
        self.close()
        
    def close(self):
        if self.publisher:
            self.publisher.close()
            self.publisher.connection.close()
        self.publisher = None
        
    def _init_sendtask(self, taskname):
        # Try to get the Task class.  The class is required if we're to record 
        # 'sent' times.
        try:
            taskcls = registry.tasks[taskname]
            self.send_task = taskcls.apply_async
            self.ignores_results = taskcls.ignore_result
            self.publisher = taskcls.get_publisher()
        except registry.tasks.NotRegistered:
            s = 'Unable to retrieve task class.  '
            s += 'Using app.send_task method instead.'
            print s
            send_task = app_or_default().send_task
            self.send_task = functools.partial(send_task, taskname)
        
    def __call__(self):
        publisher = None
        if self.publisher:
            publisher = self.publisher
        return self.send_task(args=self.args, kwargs=self.kwargs, 
                              publisher=publisher, **self.options)
                              
                              
class TimeLoop(object):
    def __init__(self, runfor):
        self.sleep_fudge_factor = 0.1
        self.start = time.time()
        self.endtime = self.start + runfor
        self.next_dispatch = self.start
        
    def elapsed(self):
        return time.time() - self.start
        
    def increment(self, offset):
        self.next_dispatch += offset
        self.next_dispatch = min(self.endtime, self.next_dispatch)
        
    def wait(self):
        next_dispatch = self.next_dispatch
        sleep_time = next_dispatch - (time.time()+self.sleep_fudge_factor)
        if sleep_time > 0.:
            time.sleep(sleep_time)
        while time.time() < next_dispatch:
            # wait for next launch
            pass
            
    def finished(self):
        return time.time() >= self.endtime


def commit(obj, **kwargs):
    for k,v in kwargs.iteritems():
        setattr(obj, k, v)
    obj.save()


def demo_dispatch(taskname, id, runfor, rate, options=None, args=None, kwargs=None):
    print 'celerymanagement.demo_dispatch::  task: {0}'.format(taskname)
    
    ignores_results = False
    
    with ApplyAsyncWrapper(taskname, options, args, kwargs) as apply_async:
        ignores_results = apply_async.ignores_results
        obj = TaskDemoGroup(uuid=id, name=taskname, completed=False, 
                            errors_on_send=0, timestamp=datetime.datetime.now(),
                            requested_rate=rate, requested_runfor=runfor)
        obj.save()
        
        count = 0
        errors_on_send = 0
        errors_on_result = 0
        results = []
        
        # the loop...
        loop = TimeLoop(runfor)
        while not loop.finished():
            
            try:
                r = apply_async()
                results.append(r)
                count += 1
            except:
                print 'Caught exception while trying to send task.'
                traceback.print_exc()
                errors_on_send += 1
                commit(obj, errors_on_send=errors_on_send)
                break
            
            if (count % TASKDEMO_COMMIT_EVERY) == 0:
                commit(obj, elapsed=loop.elapsed(), tasks_send=count, 
                          errors_on_send=errors_on_send)
            
            loop.increment(random.expovariate(rate))
            loop.wait()
        
        total_time = loop.elapsed()
        commit(obj, elapsed=total_time, tasks_sent=count, 
                    errors_on_send=errors_on_send, 
                    timestamp=datetime.datetime.now())
    
    # We must clear the results.  If a task produces results, those results 
    # stick around in the system until they're read.
    if not ignores_results:
        msg = 'celerymanagement.demo_dispatch::  '
        msg += 'clearing results (this may take a while).'
        print msg
        errors_on_result = clear_results(results)
        
    commit(obj, errors_on_result=errors_on_result, completed=True, 
              timestamp=datetime.datetime.now())
    
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
