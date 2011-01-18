import datetime
import time

from celerymanagementapp.stats import calculate_throughputs, calculate_runtimes
from celerymanagementapp.testutil import tasks #simple_test

from celerymanagementapp.tests_celery import base


class CalculateThroughput_TestCase(base.CeleryManagement_DBTestCaseBase):
    use_default_procs = True
    def test_oneTask(self):
        taskname = None
        tasks.simple_test.apply_async()
        time.sleep(4.0)
        now = datetime.datetime.now()
        timerange = (now-datetime.timedelta(seconds=45), now)
        interval = 5
        seq = calculate_throughputs(taskname, timerange, interval)
        
        ##print seq
        self.assertEquals(len(seq),9)  # 9 = 45/5
        self.assertTrue(sum(seq) > 0.)
    

# class CalculateRuntimes_TestCase(base.CeleryManagement_DBTestCaseBase):
    # def test_oneTask(self):
        # taskname = None
        # tasks.simple_test.apply_async()
        # time.sleep(1.0)
        # now = datetime.datetime.now()
        # kwargs = {
            # 'runtime_range': (0.,10.),
            # 'bin_count': 10,
            # }
        # seq = calculate_runtimes(taskname, **kwargs)
        
        # self.assertEquals(len(seq),10)
        # interval0 = seq[0][0]
        # self.assertAlmostEqual(interval0[0], 0.)
        # self.assertAlmostEqual(interval0[1], 1.)
        # self.assertTrue(sum(item[1] for item in seq) > 0)
    

