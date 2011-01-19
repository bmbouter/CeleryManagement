import time
import logging

from celery.task.control import broadcast, inspect

from celerymanagementapp.policy import api
from celerymanagementapp.policy import util

from celerymanagementapp.testutil import process
from celerymanagementapp.tests_celery import base


class PolicyTaskApi_TestCase(base.CeleryManagement_DBTestCaseBase):
    def setUp(self):
        super(PolicyTaskApi_TestCase, self).setUp()
        try:
            print 'Launching celeryd...'
            self.celeryd = process.DjCeleryd(log='celeryd.log.txt', loglevel='DEBUG')
            print 'Launching cmrun...'
            self.cmrun = process.CMRun(freq=0.1, log='celeryev.log.txt', loglevel='DEBUG')
            time.sleep(2.0)
        except Exception:
            print 'Error encountered while starting celeryd and/or cmrun.'
            if self.celeryd and not self.celeryd.is_stopped():
                self.celeryd.close()
                self.celeryd.wait()
            if self.cmrun and not self.cmrun.is_stopped():
                self.cmrun.close()
                self.cmrun.wait()
            raise
        
    def tearDown(self):
        super(PolicyTaskApi_TestCase, self).tearDown()
        print ''
        print 'Terminating cmrun...'
        self.cmrun.close()
        self.cmrun.wait()
        print 'Terminating celeryd...'
        self.celeryd.close()
        self.celeryd.wait()
        
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
    
    def test_routing_key(self):
        taskname = 'celerymanagementapp.testutil.tasks.simple_test'
        tasks = api.TasksCollectionApi()
        self.assertEquals(None, tasks[taskname].routing_key)
        tasks[taskname].routing_key = 'mykey'
        self.assertEquals('mykey', tasks[taskname].routing_key)
        
        r = self.broadcast('get_task_settings', arguments={'tasknames':[taskname],'setting_names':['routing_key']})
        self.assertEquals('mykey', r[taskname]['routing_key'])
        

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
        r = self.broadcast('get_task_settings', arguments={'tasknames':[taskname],'setting_names':[settingname]})
        return r[taskname][settingname]
        
    def task_setting_is_undefined(self, taskname, settingname):
        r = self.broadcast('get_task_settings', arguments={'tasknames':[taskname],'setting_names':[settingname]})
        return settingname not in r[taskname]
        
    def test_restore(self):
        taskname = 'celerymanagementapp.testutil.tasks.simple_test'
        with process.ProcessSequence() as procs:
            procs.add('celeryd', process.DjCeleryd, log='celeryd.log.txt')
            procs.add('cmrun', process.CMRun, freq=1.0, log='celeryev.log.txt')
            time.sleep(1.0)
            
            tasks = api.TasksCollectionApi()
            self.assertTrue(self.task_setting_is_undefined(taskname, 'routing_key'))
            tasks[taskname].routing_key = 'mykey'
            self.assertEquals('mykey', self.get_task_setting(taskname, 'routing_key'))
            
            procs.close('cmrun')
            # after closing cmrun, any changes should be undone
            self.assertTrue(self.task_setting_is_undefined(taskname, 'routing_key'), 
                            'setting = {0}'.format(self.get_task_setting(taskname, 'routing_key'))
                            )
            


