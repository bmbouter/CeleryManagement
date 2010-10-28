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
    
        
        
        
        



