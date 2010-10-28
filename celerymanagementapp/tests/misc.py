import datetime
import time

from celery.task import control as celerycontrol

from celerymanagementapp.views import calculate_throughputs
from celerymanagementapp.testutil import tasks

from celerymanagementapp.tests import base


class TaskContextManager(object):
    def __enter__(self):
        pass
    def __exit__(self, exc_type, exc_val, exc_tb):
        celerycontrol.discard_all()


class CalculateThroughput_TestCase(base.CeleryManagement_DBTestCaseBase):
    def test_basic(self):
        with TaskContextManager():
            taskname = None
            now = datetime.datetime.now()
            timerange = (now-datetime.timedelta(seconds=45), now)
            interval = 5
            seq = calculate_throughputs(taskname, timerange, interval)
            
            self.assertEquals(len(seq),9)  # 9 = 45/5
            self.assertEquals(sum(seq), 0.)
    
    def test_single_task(self):
        # Dispatch task, then make sure *something* shows up in the throughput 
        # results.
        with TaskContextManager():
            print 'enter time:             {0}'.format(datetime.datetime.now())
            tasks.simple_test.apply_async()
            time.sleep(5.)
            taskname = 'celerymanagementapp.testutil.tasks.simple_test'
            now = datetime.datetime.now()
            timerange = (now-datetime.timedelta(seconds=120), now)
            interval = 5
            seq = calculate_throughputs(taskname, timerange, interval)
            print 'after throughput time:  {0}'.format(datetime.datetime.now())
            
            self.assertEquals(len(seq),24)  # 24 = 120/5
            self.assertTrue(sum(seq) > 0., 'failed: {0} > 0.'.format(sum(seq)))
        
        
        
        



