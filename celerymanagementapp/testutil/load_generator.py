import time
import random

from celery.task import control


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
        elapsed = time.time() - start
        return count, elapsed


def generate_load(tasks, expected_rate, burst_size, runtime):
    with LoadGenerator(tasks, expected_rate, burst_size) as gen:
        return gen.run(runtime)




