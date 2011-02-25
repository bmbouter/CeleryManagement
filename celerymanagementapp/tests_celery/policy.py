import time
import logging
import os

from celery.task.control import broadcast, inspect

from celerymanagementapp.policy import api, signals, util

from celerymanagementapp.testutil import process
from celerymanagementapp.tests_celery import base

LOGLEVEL = 'DEBUG'


class PolicyApi_TestCaseBase(base.CeleryManagement_DBTestCaseBase):
    hostname = None
    def _launch_celeryd(self):
        ##print 'Launching celeryd...'
        ##self.celeryd = process.DjCeleryd(log='celeryd.log.txt', hostname=self.hostname)
        
        self.procs.add('celeryd', process.DjCeleryd, log='celeryd.log.txt', 
                       hostname=self.hostname, loglevel=LOGLEVEL, env=os.environ)
        
    def _launch_cmrun(self):
        ##print 'Launching cmrun...'
        ##self.cmrun = process.CMRun(freq=0.1, log='celeryev.log.txt')
        
        self.procs.add('cmrun', process.CMRun, freq=0.1, log='celeryev.log.txt', 
                       loglevel=LOGLEVEL, env=os.environ)
        
    def _terminate_celeryd(self):
        ##print 'Terminating celeryd...'
        self.procs.close('celeryd')
        ##self.celeryd.close()
        ##self.celeryd.wait()
        
    def _terminate_cmrun(self):
        ##print 'Terminating cmrun...'
        self.procs.close('cmrun')
        ##self.cmrun.close()
        ##self.cmrun.wait()
    
    def setUp(self):
        super(PolicyApi_TestCaseBase, self).setUp()
        os.environ['PYTHONWARNINGS'] = 'ignore'  # silence warnings
        self.procs = process.ProcessSequence()
        self._launch_celeryd()
        self._launch_cmrun()
        # try:
            # self._launch_celeryd()
            # self._launch_cmrun()
            # time.sleep(2.0)
        # except Exception:
            # print 'Error encountered while starting celeryd and/or cmrun.'
            # if self.celeryd and not self.celeryd.is_stopped():
                # self.celeryd.close()
                # self.celeryd.wait()
            # if self.cmrun and not self.cmrun.is_stopped():
                # self.cmrun.close()
                # self.cmrun.wait()
            # raise
        
    def tearDown(self):
        super(PolicyApi_TestCaseBase, self).tearDown()
        print ''
        self._terminate_cmrun()
        self._terminate_celeryd()
        self.procs.close()
        del os.environ['PYTHONWARNINGS']
        
    def broadcast(self, name, *args, **kwargs):
        if 'reply' not in kwargs:
            kwargs['reply'] = True
        result = broadcast(name, *args, **kwargs)
        result = util._merge_broadcast_result(result)  # turn it into a single dict
        result = util._condense_broadcast_result(result)  # remove worker key
        for k,v in result.iteritems():
            if isinstance(v, dict) and 'error' in v:
                raise RuntimeError('Found error in broadcast()')
        return result


class PolicyTaskApi_TestCase(PolicyApi_TestCaseBase):
    
    def test_routing_key(self):
        taskname = 'celerymanagementapp.testutil.tasks.simple_test'
        dispatcher = signals.Dispatcher()
        try:
            tasks = api.TasksCollectionApi(dispatcher)
            self.assertEquals(None, tasks[taskname].routing_key)
            tasks[taskname].routing_key = 'mykey'
            self.assertEquals('mykey', tasks[taskname].routing_key)
            
            r = self.broadcast('get_task_settings', arguments={'tasknames':[taskname],'setting_names':['routing_key']})
            self.assertEquals('mykey', r[taskname]['routing_key'])
        finally:
            dispatcher.close()
        

class PolicyWorkerApi_TestCase(PolicyApi_TestCaseBase):
    hostname = 'worker1'
    
    def test_prefetch(self):
        ##import os
        ##print 'COVERAGE_PROCESS_START: {0}'.format(os.environ.get('COVERAGE_PROCESS_START','COVERAGE_PROCESS_START is not set'))
        
        workername = self.hostname
        workers = api.WorkersCollectionApi()
        prefetch = workers[workername].prefetch.get()
        workers[workername].prefetch.increment()
        self.assertEquals(prefetch+1, workers[workername].prefetch.get())
        workers[workername].prefetch.decrement()
        self.assertEquals(prefetch, workers[workername].prefetch.get())
    
    def test_subprocesses(self):
        workername = self.hostname
        workers = api.WorkersCollectionApi()
        subprocesses = workers[workername].subprocesses.get()
        workers[workername].subprocesses.increment()
        self.assertEquals(subprocesses+1, workers[workername].subprocesses.get())
        workers[workername].subprocesses.decrement()
        self.assertEquals(subprocesses, workers[workername].subprocesses.get())







class PolicyRestoreTaskSettings_TestCase(base.CeleryManagement_DBTestCaseBase):
        
    def broadcast(self, name, *args, **kwargs):
        if 'reply' not in kwargs:
            kwargs['reply'] = True
        result = broadcast(name, *args, **kwargs)
        result = util._merge_broadcast_result(result)  # turn it into a single dict
        result = util._condense_broadcast_result(result)  # remove worker key
        for k,v in result.iteritems():
            if isinstance(v, dict) and 'error' in v:
                raise RuntimeError('Found error in broadcast()')
        return result
    
    def get_task_setting(self, taskname, settingname):
        x = ''
        r = self.broadcast('get_task_settings', arguments={'tasknames':[taskname],'setting_names':[settingname]})
        if settingname in r[taskname]:
            x = r[taskname][settingname]
        return x
        
    def task_setting_is_undefined(self, taskname, settingname):
        r = self.broadcast('get_task_settings', arguments={'tasknames':[taskname],'setting_names':[settingname]})
        return settingname not in r[taskname]
        
    def test_restore(self):
        taskname = 'celerymanagementapp.testutil.tasks.simple_test'
        with process.ProcessSequence() as procs:
            dispatcher = signals.Dispatcher()
            
            try:
                procs.add('celeryd', process.DjCeleryd, log='celeryd.log.txt', loglevel='DEBUG')
                time.sleep(2.0)
                procs.add('cmrun', process.CMRun, freq=0.1, log='celeryev.log.txt', loglevel='DEBUG')
                time.sleep(2.0)
                tasks = api.TasksCollectionApi(dispatcher)
                self.assertTrue(self.task_setting_is_undefined(taskname, 'routing_key'))
                tasks[taskname].routing_key = 'mykey'
                self.assertEquals('mykey', self.get_task_setting(taskname, 'routing_key'))
                
                time.sleep(2.0)
                procs.close('cmrun')
                time.sleep(2.0)
                # after closing cmrun, any changes should be undone
                self.assertTrue(self.task_setting_is_undefined(taskname, 'routing_key'), 
                                'setting = "{0}"'.format(self.get_task_setting(taskname, 'routing_key'))
                                )
                ##print time.ctime()
            finally:
                dispatcher.close()
            








