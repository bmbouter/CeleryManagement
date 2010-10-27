import datetime

from celerymanagementapp.views import calculate_throughputs

from celerymanagementapp.tests import base

class CalculateThroughput_TestCase(base.CeleryManagement_DBTestCaseBase):
    def test_basic(self):
        taskname = None
        now = datetime.datetime.now()
        timerange = (now-datetime.timedelta(seconds=45), now)
        interval = 5
        seq = calculate_throughputs(taskname, timerange, interval)
        
        self.assertEquals(len(seq),9)  # 9 = 45/5




