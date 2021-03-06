import json
import datetime

from django.core.urlresolvers import reverse as urlreverse
from django.core.exceptions import ObjectDoesNotExist

from celerymanagementapp import timeutil
from celerymanagementapp.tests import base, testcase_settings
from celerymanagementapp.models import OutOfBandWorkerNode, Provider
from celerymanagementapp.models import PolicyModel


class XYDataView_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_runtimes']
    
    def test_basic(self):
        url = urlreverse('celerymanagementapp.dataviews.task_xy_dataview')
        json_request = {
            "segmentize": {
                "field": "taskname",
                "method": [ "all" ],
            },
            "aggregate": [
                {
                    "field": "runtime",
                    "methods": ["average"]
                }
            ]
        }
        expected_output = {
            'data': [
                [u'task1', [{'fieldname': 'runtime', 'methods': [{'name': 'average', 'value': 2.6}] }] ],
                [u'task2', [{'fieldname': 'runtime', 'methods': [{'name': 'average', 'value': 2.5}] }] ],
                ]
            }
        rawjson = json.dumps(json_request)
        with self.scoped_login('test_user','password'):
            response = self.client.post(url, rawjson, content_type='application/json')
        output = json.loads(response.content)
        
        self.assertEquals(expected_output, output)
        
    def test_regression1(self):
        url = urlreverse('celerymanagementapp.dataviews.task_xy_dataview')
        json_request = {
            "segmentize": {
                "field": "sent",
                "method": [ "range", {'min': 1299691750000, 'max': 1299702556000, 'interval': 3600000} ],
            },
            "aggregate": [
                {
                    "field": "count",
                    "methods": ["average"]
                }
            ]
        }
        json_request = {"segmentize":{"field":"sent","method":["range",{"min":1299792588000,"max":1299792598000,"interval":3600000}]},"aggregate":[{"field":"count","methods":["average"]}]}
        rawjson = json.dumps(json_request)
        with self.scoped_login('test_user','password'):
            response = self.client.post(url, rawjson, content_type='application/json')
        output = json.loads(response.content)
        
        data = output['data']
        self.assertTrue(data[0][1] != float('nan'))
        ##import pprint
        ##pprint.pprint(data)
        
        
class TaskXYMetadata_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_runtimes']
    
    def test_basic(self):
        url = urlreverse('celerymanagementapp.dataviews.task_xy_metadata')
        with self.scoped_login('test_user','password'):
            response = self.client.get(url)
        meta = json.loads(response.content)
        
        expected_keys = ['taskname','state','task_id','worker', 
                         'runtime','waittime','totaltime',
                         'tstamp','sent','received','started','succeeded','failed',
                         'routing_key','expires','result','eta',
                         'count',]
        expected_keys.sort()
        keys = meta.keys()
        keys.sort()
        self.assertEquals(expected_keys, keys)
        
        # taskname
        self.assertEquals({
            'type':         'string',
            'allow_null':   False,
            'segmentize':   {'methods': ['each', 'values', 'all',]},
            'aggregate':    {'methods': ['enumerate',]},
            },
            meta['taskname'])
            
        # worker
        self.assertEquals({
            'type':         'string',
            'allow_null':   False,
            'segmentize':   {'methods': ['each', 'values', 'all',]},
            'aggregate':    {'methods': ['enumerate',]},
            },
            meta['worker'])
        
        # runtime
        self.assertEquals({
            'type':         'elapsed_time',
            'allow_null':   False,
            'segmentize':   {'methods': ['each', 'range',]},
            'aggregate':    {'methods': ['average', 'min', 'max', 'sum', 'variance',]},
            },
            meta['runtime'])
        
        # waittime
        self.assertEquals({
            'type':         'elapsed_time',
            'allow_null':   True,
            'segmentize':   {'methods': ['each', 'range',]},
            'aggregate':    {'methods': ['average', 'min', 'max', 'sum', 'variance',]},
            },
            meta['waittime'])
        
        # tstamp
        self.assertEquals({
            'type':         'datetime',
            'allow_null':   False,
            'segmentize':   {'methods': ['each', 'range',]},
            'aggregate':    {'methods': ['average', 'min', 'max', 'sum', 'variance',]},
            },
            meta['tstamp'])
        
        # started
        self.assertEquals({
            'type':         'datetime',
            'allow_null':   True,
            'segmentize':   {'methods': ['each', 'range',]},
            'aggregate':    {'methods': ['average', 'min', 'max', 'sum', 'variance',]},
            },
            meta['started'])
        
        # result
        self.assertEquals({
            'type':         'string',
            'allow_null':   True,
            'segmentize':   {'methods': ['each', 'values', 'all',]},
            'aggregate':    {'methods': ['enumerate',]},
            },
            meta['result'])
        
        # count
        self.assertEquals({
            'type':         'int',
            'allow_null':   False,
            'segmentize':   {'methods': []},
            'aggregate':    {'methods': ['count',]},
            },
            meta['count'])
        

class PendingTaskCount_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_pending_taskcount']
    
    def test_basic(self):
        url = urlreverse('celerymanagementapp.dataviews.pending_task_count_dataview', kwargs={'name': 'all'})
        expected_output = {
            'task1': 2,
            'task2': 1,
            }
        
        with self.scoped_login('test_user','password'):
            response = self.client.post(url, '', content_type='application/json')
        output = json.loads(response.content)
        
        self.assertEquals(expected_output, output)

class TasksPerWorker_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_pending_taskcount']
    
    def test_basic(self):
        url = urlreverse('celerymanagementapp.dataviews.tasks_per_worker_dataview', kwargs={'name':'all'})
        expected_output = {
            'task1': {'worker1': 3, 'worker2': 2}, 
            'task2': {'worker1': 2, 'worker2': 2},
            }
        with self.scoped_login('test_user','password'):
            response = self.client.post(url, '', content_type='application/json')
        output = json.loads(response.content)
        
        self.assertEquals(expected_output, output)



class WorkerList_TestCase(base.CeleryManagement_DBTestCaseBase):
    
    def test_basic(self):
        from django.conf import settings
        from celerymanagementapp import dataviews
        # Note: modifying Django settings at runtime is in general a bad idea.
        old_use_mode = settings.CELERYMANAGEMENTAPP_INFRASTRUCTURE_USE_MODE
        settings.CELERYMANAGEMENTAPP_INFRASTRUCTURE_USE_MODE = 'dynamic'
        old_test_flag = dataviews.GET_WORKERS_LIVE_ENABLE_TEST
        dataviews.GET_WORKERS_LIVE_ENABLE_TEST = ['worker1']

        try:
            url = urlreverse('celerymanagementapp.dataviews.worker_list_dataview')
            expected_output = ['worker1']
            response = self.client.post(url, '', content_type='application/json')
            output = json.loads(response.content)
            self.assertEquals(expected_output, output)

        finally:
            dataviews.GET_WORKERS_LIVE_ENABLE_TEST = old_test_flag
            settings.CELERYMANAGEMENTAPP_INFRASTRUCTURE_USE_MODE = old_use_mode
            
    def test_static1(self):
        from django.conf import settings
        # Note: modifying Django settings at runtime is in general a bad idea.
        old_use_mode = settings.CELERYMANAGEMENTAPP_INFRASTRUCTURE_USE_MODE
        settings.CELERYMANAGEMENTAPP_INFRASTRUCTURE_USE_MODE = 'static'

        try:
            OutOfBandWorkerNode.objects.all().delete()  # try with no objects
            url = urlreverse('celerymanagementapp.dataviews.worker_list_dataview')
            expected_output = []
            response = self.client.post(url, '', content_type='application/json')
            output = json.loads(response.content)
            self.assertEquals(expected_output, output)

        finally:
            settings.CELERYMANAGEMENTAPP_INFRASTRUCTURE_USE_MODE = old_use_mode
            
        

class Configuration_TestCase(base.CeleryManagement_DBTestCaseBase):
    def setUp(self):
        super(Configuration_TestCase, self).setUp()
        self.outofbandworker_url = '/celerymanagementapp/outofbandworker/'
        self.provider_url = '/celerymanagementapp/provider/'

    def test_create_outofbandworker(self):
        f = open(testcase_settings.OUTOFBANDWORKER_SSH_KEY_FILE) #path to ssh_key file for testing
        
        with self.scoped_login('test_user','password'):
            response = self.client.post(self.outofbandworker_url, {
                            'ip' : testcase_settings.OUTOFBANDWORKER_IP,
                            'celeryd_username' : testcase_settings.OUTOFBANDWORKER_USERNAME,
                            'ssh_key' : f,
                            'celeryd_start_cmd' : testcase_settings.OUTOFBANDWORKER_CELERYD_START ,
                            'celeryd_stop_cmd' : testcase_settings.OUTOFBANDWORKER_CELERYD_STOP,
                            'celeryd_status_cmd' : testcase_settings.OUTOFBANDWORKER_CELERYD_STATUS,
                            'active' : 'on',
                                })
        f.close()
        self.assertEquals(response.status_code, 200)
        outofbandworkers = OutOfBandWorkerNode.objects.all()
        self.assertEquals(len(outofbandworkers), 1)

    def test_create_provider(self):
        f = open(testcase_settings.PROVIDER_SSH_KEY_FILE) #path to ssh_key file for testing
        
        with self.scoped_login('test_user','password'):
            response = self.client.post(self.provider_url, {
                            'provider_user_id' : testcase_settings.PROVIDER_USER_ID,
                            'provider_key' : testcase_settings.PROVIDER_KEY,
                            'provider_name' : testcase_settings.PROVIDER_NAME,
                            'image_id' : testcase_settings.PROVIDER_IMAGE_ID,
                            'celeryd_username' : testcase_settings.OUTOFBANDWORKER_USERNAME,
                            'ssh_key' : f,
                            'celeryd_start_cmd' : testcase_settings.OUTOFBANDWORKER_CELERYD_START ,
                            'celeryd_stop_cmd' : testcase_settings.OUTOFBANDWORKER_CELERYD_STOP,
                            'celeryd_status_cmd' : testcase_settings.OUTOFBANDWORKER_CELERYD_STATUS,
                            'active' : 'on',
                                })
        f.close()
        self.assertEquals(response.status_code, 200)
        providers = Provider.objects.all()
        self.assertEquals(len(providers), 1)


class PolicyCreate_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_policy']
    
    def test_basic(self):
        now = datetime.datetime.now()
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_create')
        post_data = {
            'name': 'another_policy',
            'source': 'policy:\n schedule:\n  True\n apply:\n  True',
            'enabled': True,
        }
        
        with self.scoped_login('test_user','password'):
            response = self.client.post(url, post_data)
        output = json.loads(response.content)
        
        self.assertContains(response, 'Policy successfully created.')
        self.assertEquals(model_count + 1, PolicyModel.objects.all().count())
        id = model_count + 1
        obj = PolicyModel.objects.get(id=id)
        self.assertTrue(obj.modified >= now)
        self.assertEquals(obj.name, 'another_policy')
        self.assertEquals(obj.source, 'policy:\n schedule:\n  True\n apply:\n  True')
        self.assertEquals(obj.enabled, True)
        self.assertEquals(obj.last_run_time, None)
        
    def test_disabled(self):
        # Create a Policy that is initially disabled.
        now = datetime.datetime.now()
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_create')
        post_data = {
            'name': 'another_policy',
            'source': 'policy:\n schedule:\n  True\n apply:\n  True',
            'enabled': False,
        }
        
        with self.scoped_login('test_user','password'):
            response = self.client.post(url, post_data)
        output = json.loads(response.content)
        
        self.assertContains(response, 'Policy successfully created.')
        self.assertEquals(model_count + 1, PolicyModel.objects.all().count())
        id = model_count + 1
        obj = PolicyModel.objects.get(id=id)
        self.assertTrue(obj.modified >= now)
        self.assertEquals(obj.name, 'another_policy')
        self.assertEquals(obj.source, 'policy:\n schedule:\n  True\n apply:\n  True')
        self.assertEquals(obj.enabled, False)
        self.assertEquals(obj.last_run_time, None)
        
    def test_nocompile(self):
        # The policy contains source code that is not in the expected format.
        from celerymanagementapp.policy import exceptions
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_create')
        post_data = {
            'name': 'nocompile_policy',
            'source': 'This should not compile',  # not legal policy source
            'enabled': True,
        }
        
        with self.scoped_login('test_user','password'):
            response = self.client.post(url, post_data)
        output = json.loads(response.content)
        
        self.assertTrue('failure' in output)
        self.assertEquals('source', output['failure'][2]['field'])
        experror = '  File "<unknown>", line 1\n    This should not compile\n    ^\nPolicySyntaxError: expected "policy", found "This"\n'
        self.assertEquals(experror, output['failure'][2]['error'][0])
        # no model objects should have been created
        self.assertEquals(model_count, PolicyModel.objects.all().count())
        
    def test_duplicate_name(self):
        # A policy with the given name already exists.  No new policy should be 
        # created.
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_create')
        post_data = {
            'name': 'normal_policy',  # policy with this name already exists
            'source': 'policy:\n schedule:\n  True\n apply:\n  True',
            'enabled': True,
        }
        with self.scoped_login('test_user','password'):
            response = self.client.post(url, post_data)
        output = json.loads(response.content)
        
        self.assertTrue('failure' in output)
        self.assertEquals('name', output['failure'][0]['field'])
        self.assertEquals('Policy model with this Name already exists.', output['failure'][0]['error'][0])
        # no model objects should have been created
        self.assertEquals(model_count, PolicyModel.objects.all().count())
        
    def test_request_missing_key(self):
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_create')
        post_data = {
            # Missing 'name' key.
            'source': 'policy:\n schedule:\n  True\n apply:\n  True',
            'enabled': True,
        }
        with self.scoped_login('test_user','password'):
            response = self.client.post(url, post_data)
        output = json.loads(response.content)
        
        self.assertTrue('failure' in output)
        self.assertEquals('name', output['failure'][0]['field'])
        self.assertEquals('This field is required.', output['failure'][0]['error'][0])
        # no model objects should have been created
        self.assertEquals(model_count, PolicyModel.objects.all().count())
        
        

class PolicyModify_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_policy']
    
    def test_basic(self):
        D = datetime.datetime
        now = datetime.datetime.now()
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_modify', 
                         kwargs={'policy_id': 1} )
        post_data = {
            'name': 'another_policy',
            'source': 'policy:\n schedule:\n  True\n apply:\n  True',
            'enabled': True,
        }
            
        self.assertNotEqual('another_policy', PolicyModel.objects.get(id=1).name)
        
        with self.scoped_login('test_user','password'):
            response = self.client.post(url, post_data)
        output = json.loads(response.content)
        
        self.assertEquals('Policy successfully updated.', output)
        self.assertEquals(model_count, PolicyModel.objects.all().count())
        obj = PolicyModel.objects.get(id=1)
        self.assertTrue(obj.modified >= now)
        self.assertEquals('another_policy', obj.name)
        self.assertEquals(obj.name, 'another_policy')
        self.assertEquals(obj.source, 'policy:\n schedule:\n  True\n apply:\n  True')
        self.assertEquals(obj.enabled, True)
        self.assertEquals(obj.last_run_time, D(2010,1,4,hour=12))
        
    def test_nonexistent_id(self):
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_modify', 
                         kwargs={'policy_id': model_count+1} )
        json_request = {
            'name': 'another_policy',
            'source': 'policy:\n schedule:\n  True\n apply:\n  True',
            'enabled': True,
        }
        
        with self.scoped_login('test_user','password'):
            response = self.client.post(url, json_request)
        output = json.loads(response.content)
        
        self.assertTrue('failure' in output)
        em = 'No Policy with the given ID ({0}) was found.'.format(model_count+1)
        self.assertEquals(em, output['failure'])
        self.assertEquals(model_count+1, int(output['id']))
        # no model objects should have been created
        self.assertEquals(model_count, PolicyModel.objects.all().count())
        
    def test_duplicate_name(self):
        # A policy with the given name already exists.  No new policy should be 
        # created.
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_modify', 
                         kwargs={'policy_id': 2} )
        post_data = {
            'name': 'normal_policy',  # policy with this name already exists
            'source': 'policy:\n schedule:\n  True\n apply:\n  True',
            'enabled': True,
        }
        with self.scoped_login('test_user','password'):
            response = self.client.post(url, post_data)
        output = json.loads(response.content)
        
        self.assertTrue('failure' in output)
        self.assertEquals('name', output['failure'][0]['field'])
        self.assertEquals('Policy model with this Name already exists.', output['failure'][0]['error'][0])
        # no model objects should have been created
        self.assertEquals(model_count, PolicyModel.objects.all().count())
        
class PolicyDelete_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_policy']
    
    def test_basic(self):
        D = datetime.datetime
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_delete', 
                         kwargs={'policy_id': 1} )
        
        with self.scoped_login('test_user','password'):
            response = self.client.post(url, {})
        output = json.loads(response.content)
        
        self.assertEquals('Policy successfully deleted.', output)
        self.assertEquals(model_count-1, PolicyModel.objects.all().count())
        self.assertRaises(ObjectDoesNotExist, PolicyModel.objects.get, id=1)
    
    def test_nonexistent_id(self):
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_delete', 
                         kwargs={'policy_id': model_count+1} )
        
        with self.scoped_login('test_user','password'):
            response = self.client.post(url, {})
        output = json.loads(response.content)
        
        self.assertTrue('failure' in output)
        self.assertEquals('PolicyModel matching query does not exist.', output['failure'])
        # nothing was deleted
        self.assertEquals(model_count, PolicyModel.objects.all().count())
        
        
class PolicyGet_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_policy']
    
    def test_basic(self):
        D = datetime.datetime
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_get', 
                         kwargs={'id': 1} )
        
        expected_output = {
            'success': True,
            'record': {
                'id': 1, 
                'name': 'normal_policy', 
                'source': 'policy:\n    schedule:\n        crontab()\n    apply:\n        True', 
                'enabled': True, 
                'modified': timeutil.datetime_from_python(D(2010,1,4,hour=12)), 
                'last_run_time': timeutil.datetime_from_python(D(2010,1,4,hour=12)),
                },
            'error_info': {
                'compile_error': False, 
                'type': '', 
                'msg': '', 
                'traceback': '',
                },
            }
        with self.scoped_login('test_user','password'):
            response = self.client.post(url, '', content_type='application/json')
        output = json.loads(response.content)
        
        self.assertEquals(expected_output, output)
        self.assertEquals(model_count, PolicyModel.objects.all().count())
    
    def test_nonexistent_id(self):
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_get', 
                         kwargs={'id': model_count+1} )
        
        with self.scoped_login('test_user','password'):
            response = self.client.post(url, '', content_type='application/json')
        output = json.loads(response.content)
        
        self.assertEquals(False, output['success'])
        self.assertEquals(False, output['error_info']['compile_error'])
        self.assertEquals('ObjectDoesNotExist', output['error_info']['type'])
        self.assertEquals('', output['error_info']['traceback'])
        self.assertTrue(output['error_info']['msg'])
        # nothing was changed
        self.assertEquals(model_count, PolicyModel.objects.all().count())
        
class PolicyList_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_policy']
    
    def test_basic(self):
        D = datetime.datetime
        url = urlreverse('celerymanagementapp.dataviews.policy_list')
        
        modified = timeutil.datetime_from_python(D(2010,1,4,hour=12))
        last_run_time = timeutil.datetime_from_python(D(2010,1,4,hour=12))
                
        expected_output = [
            {'id': 1, 'name': 'normal_policy', 'enabled': True, 'modified': modified, 'last_run_time': last_run_time,},
            {'id': 2, 'name': 'second_policy', 'enabled': True, 'modified': modified, 'last_run_time': last_run_time,},
        ]
            
        with self.scoped_login('test_user','password'):
            response = self.client.post(url, '', content_type='application/json')
        output = json.loads(response.content)
        
        self.assertEquals(expected_output, output)











