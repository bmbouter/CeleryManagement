import datetime
import time

from celerymanagementapp.stats import calculate_throughputs, calculate_runtimes

from celerymanagementapp.tests import base


class CalculateThroughputEmpty_TestCase(base.CeleryManagement_DBTestCaseBase):
    def test_basic(self):
        taskname = None
        now = datetime.datetime.now()
        timerange = (now-datetime.timedelta(seconds=45), now)
        interval = 5
        seq = calculate_throughputs(taskname, timerange, interval)
        
        self.assertEquals(len(seq),9)  # 9 = 45/5
        self.assertEquals(sum(seq), 0.)
    
class CalculateThroughput_TestCase(base.CeleryManagement_DBTestCaseBase):
    #fixtures = ['']
    
    # params:
    #   taskname - None, known task, unknown task
    #   timerange - (None,None), (time,None), (None,time), (time,time), wrong types?
    #   interval - 0, 1, ...?
    
    pass

class CalculateRuntimesEmpty_TestCase(base.CeleryManagement_DBTestCaseBase):
    pass
    #def test_basic(self):
    #    pass
        
class CalculateExplicitRuntimes_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_runtimes']
    
    # EXPLICIT params:
    #   taskname - None, known task, unknown task
    #   search_range - (None,None), (time,None), (None,time), (time,time), wrong types?
    #   runtime_range - 
    #   bin_size - 
    #   bin_count - None, 0, 1, 20, ...?
    #   
    
    def test_known_taskname(self):
        bins = calculate_runtimes(taskname='task1', runtime_range=(0.5,5.5), bin_count=5)
        self.assertEquals(len(bins), 5)
        self.assertEquals(bins[0], ((0.5,1.5),1))
        self.assertEquals(bins[1], ((1.5,2.5),1))
        self.assertEquals(bins[2], ((2.5,3.5),2))
        self.assertEquals(bins[3], ((3.5,4.5),1))
        self.assertEquals(bins[4], ((4.5,5.5),0))
        
    def test_none_taskname(self):
        bins = calculate_runtimes(taskname=None, runtime_range=(0.5,5.5), bin_count=5)
        self.assertEquals(len(bins), 5)
        self.assertEquals(bins[0], ((0.5,1.5),2))
        self.assertEquals(bins[1], ((1.5,2.5),2))
        self.assertEquals(bins[2], ((2.5,3.5),3))
        self.assertEquals(bins[3], ((3.5,4.5),2))
        self.assertEquals(bins[4], ((4.5,5.5),0))
        
    def test_unknown_taskname(self):
        bins = calculate_runtimes(taskname='unknown_task', runtime_range=(0.5,5.5), bin_count=5)
        self.assertEquals(len(bins), 5)
        self.assertEquals(bins[0], ((0.5,1.5),0))
        self.assertEquals(bins[1], ((1.5,2.5),0))
        self.assertEquals(bins[2], ((2.5,3.5),0))
        self.assertEquals(bins[3], ((3.5,4.5),0))
        self.assertEquals(bins[4], ((4.5,5.5),0))
        
    def test_min_searchrange(self):
        t0 = datetime.datetime(2010, 1, 1, hour=13, minute=0, second=0)
        bins = calculate_runtimes(None, search_range=(t0,None), runtime_range=(0.5,5.5), bin_count=5)
        self.assertEquals(len(bins), 5)
        self.assertEquals(bins[0], ((0.5,1.5),1))
        self.assertEquals(bins[1], ((1.5,2.5),1))
        self.assertEquals(bins[2], ((2.5,3.5),3))
        self.assertEquals(bins[3], ((3.5,4.5),2))
        self.assertEquals(bins[4], ((4.5,5.5),0))
        
    def test_max_searchrange(self):
        t1 = datetime.datetime(2010, 1, 1, hour=14, minute=0, second=0)
        bins = calculate_runtimes(None, search_range=(None,t1), runtime_range=(0.5,5.5), bin_count=5)
        self.assertEquals(len(bins), 5)
        self.assertEquals(bins[0], ((0.5,1.5),2))
        self.assertEquals(bins[1], ((1.5,2.5),2))
        self.assertEquals(bins[2], ((2.5,3.5),2))
        self.assertEquals(bins[3], ((3.5,4.5),0))
        self.assertEquals(bins[4], ((4.5,5.5),0))
        
    def test_minmax_searchrange(self):
        t0 = datetime.datetime(2010, 1, 1, hour=13, minute=0, second=0)
        t1 = datetime.datetime(2010, 1, 1, hour=14, minute=0, second=0)
        bins = calculate_runtimes(None, search_range=(t0,t1), runtime_range=(0.5,5.5), bin_count=5)
        self.assertEquals(len(bins), 5)
        self.assertEquals(bins[0], ((0.5,1.5),1))
        self.assertEquals(bins[1], ((1.5,2.5),1))
        self.assertEquals(bins[2], ((2.5,3.5),2))
        self.assertEquals(bins[3], ((3.5,4.5),0))
        self.assertEquals(bins[4], ((4.5,5.5),0))
        
class CalculateAutoRuntimes_TestCase(base.CeleryManagement_DBTestCaseBase):
    #fixtures = ['']
    
    # AUTO params:
    #   taskname - None, known task, unknown task
    #   search_range - (None,None), (time,None), (None,time), (time,time), wrong types?
    #   bin_count - None(bad), 0 (bad), 1, 20, ...?
    
    pass





