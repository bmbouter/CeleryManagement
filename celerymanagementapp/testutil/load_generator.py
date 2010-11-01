import time
import random
import sys

from celery.task import control
from celery.task.base import Task as CeleryTask


class LoadGenerator(object):
    sleep_fudge_factor = 0.01
    
    def __init__(self, tasks, expected_rate=10.0, burst_size=20):
        self.tasks = []
        for task in tasks:
            self._addtask(task)
        self.expected_rate = expected_rate
        self.burst_size = burst_size
        
    def _addtask(self, task):
        if not task.ignore_result:
            raise RuntimeError('tasks must have the ignore_result option set to True.')
        self.tasks.append(task)
        
    def cleanup(self):
        # clean up queues
        n = control.discard_all()
        if n:
            print 'LoadGenerator.cleanup() purged {0} tasks.'.format(n)
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        
    def burst(self, burst_size=None):
        if not burst_size:
            burst_size = self.burst_size
        start = time.time()
        # fire tasks
        for i in xrange(burst_size):
            task = random.choice(self.tasks)
            task.apply_async()
        elapsed = time.time()-start
        actual_rate = burst_size/elapsed
        if actual_rate>self.expected_rate:
            # sleep until the expected rate is matched
            sleeptime = burst_size/self.expected_rate - elapsed - LoadGenerator.sleep_fudge_factor
            time.sleep(sleeptime)
        # return the actual rate
        return burst_size/(time.time()-start)
        
    def run(self, runtime):
        count = 0
        start = time.time()
        while (time.time()-start) < runtime:
            self.burst(self.burst_size)
            count += self.burst_size
            sys.stdout.write('.')
            sys.stdout.flush()
        elapsed = time.time() - start
        sys.stdout.write('\n')
        return count, elapsed


def generate_load(tasks, expected_rate, burst_size, runtime):
    """
        Dispatches tasks at a specified throughput and runtime.
        
        tasks: 
            A single task or an iterable of tasks.  
            
            If it is an iterable, each time a task is to be dispatched, one 
            will be chosen at random.
            
        expected_rate: 
            The expected throughput (tasks/sec).  
            
            The resulting average throughput will be approximately this value, 
            unless it is unable to launch tasks at a sufficient frequency in 
            which case the resulting throughput will be less.
            
        burst_size:
            The number of tasks to be launched between checking the throughput.
            
            A larger burst_size usually means that a higher throughput will be 
            achieved.  After a burst has completed, if the actual throughput is 
            higher than the expected, it will wait until such time has elapsed 
            to decrease the throughput to the desired level.
            
        runtime:
            The total time in seconds over which to generate the load.
            
            Basically, it will continue to fire bursts of tasks until this 
            runtime has been reached.  
            The actual runtime is always at least this value and sometimes a 
            good deal more.  When a burst finishes just short of this expected 
            time, it will launch another full burst, and this will result in an 
            elapsed time greater than the expected value.
        
        return value:
            A tuple: (total_tasks, elapsed_time).  Calculating the actual 
            throughput is simple: total_tasks / elapsed_time .
            
        All tasks must have the attribute Task.ignore_result set to True.  If 
        not, an exception will be thrown.  This is to prevent buildup of unused 
        task return values, which are otherwise saved by Celery.
        
        This function purges the task queue before returning.  This happens 
        even in the face of exceptions.
        
    """
    if isinstance(tasks, CeleryTask):
        tasks = [tasks]
    with LoadGenerator(tasks, expected_rate, burst_size) as gen:
        return gen.run(runtime)




