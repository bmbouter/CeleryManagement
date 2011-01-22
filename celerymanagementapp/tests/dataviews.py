import json
import datetime

from django.core.urlresolvers import reverse as urlreverse

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
        response = self.client.post(url, rawjson, content_type='application/json')
        output = json.loads(response.content)
        
        self.assertEquals(expected_output, output)


class Configuration_TestCase(base.CeleryManagement_TestCaseBase):
    def setUp(self):
        self.outofbandworker_url = '/celerymanagementapp/outofbandworker/'
        self.provider_url = '/celerymanagementapp/provider/'

    def test_create_outofbandworker(self):
        f = open(testcase_settings.OUTOFBANDWORKER_SSH_KEY_FILE) #path to ssh_key file for testing
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
        json_request = {
            'name': 'another_policy',
            'source': 'policy:\n schedule:\n  True\n apply:\n  True',
            'enabled': True,
        }
        
        expected_output = {
            'success': True,
            'record': {
                'id': model_count + 1, 
                'name': 'another_policy', 
                'source': 'policy:\n schedule:\n  True\n apply:\n  True', 
                'enabled': True, 
                #'modified': None, 
                'last_run_time': None,
                },
            'error_info': {
                'compile_error': False, 
                'type': '', 
                'msg': '', 
                'traceback': '',
                },
            }
        rawjson = json.dumps(json_request)
        response = self.client.post(url, rawjson, content_type='application/json')
        output = json.loads(response.content)
        
        modified = output['record'].pop('modified')
        self.assertEquals(expected_output, output)
        self.assertTrue(modified >= timeutil.datetime_from_python(now))
        self.assertEquals(model_count + 1, PolicyModel.objects.all().count())
        
    def test_disabled(self):
        # Create a Policy that is initially disabled.
        now = datetime.datetime.now()
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_create')
        json_request = {
            'name': 'another_policy',
            'source': 'policy:\n schedule:\n  True\n apply:\n  True',
            'enabled': False,
        }
        
        expected_output = {
            'success': True,
            'record': {
                'id': model_count + 1, 
                'name': 'another_policy', 
                'source': 'policy:\n schedule:\n  True\n apply:\n  True', 
                'enabled': False, 
                #'modified': None, 
                'last_run_time': None,
                },
            'error_info': {
                'compile_error': False, 
                'type': '', 
                'msg': '', 
                'traceback': '',
                },
            }
        rawjson = json.dumps(json_request)
        response = self.client.post(url, rawjson, content_type='application/json')
        output = json.loads(response.content)
        
        modified = output['record'].pop('modified')
        self.assertEquals(expected_output, output)
        self.assertTrue(modified >= timeutil.datetime_from_python(now))
        self.assertEquals(model_count + 1, PolicyModel.objects.all().count())
        
    def test_nocompile(self):
        # The policy contains source code that is not in the expected format.
        from celerymanagementapp.policy import exceptions
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_create')
        json_request = {
            'name': 'nocompile_policy',
            'source': 'This should not compile',  # not legal policy source
            'enabled': True,
        }
        rawjson = json.dumps(json_request)
        response = self.client.post(url, rawjson, content_type='application/json')
        output = json.loads(response.content)
        
        self.assertEquals(False, output['success'])
        self.assertEquals(True, output['error_info']['compile_error'])
        self.assertEquals(str(exceptions.SyntaxError), output['error_info']['type'])
        self.assertTrue(output['error_info']['msg'])
        # no model objects should have been created
        self.assertEquals(model_count, PolicyModel.objects.all().count())
        
    def test_duplicate_name(self):
        # A policy with the given name already exists.  No new policy should be 
        # created.
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_create')
        json_request = {
            'name': 'normal_policy',  # policy with this name already exists
            'source': 'policy:\n schedule:\n  True\n apply:\n  True',
            'enabled': True,
        }
        rawjson = json.dumps(json_request)
        response = self.client.post(url, rawjson, content_type='application/json')
        output = json.loads(response.content)
        
        self.assertEquals(False, output['success'])
        self.assertEquals(False, output['error_info']['compile_error'])
        self.assertEquals('DuplicateName', output['error_info']['type'])
        self.assertEquals('', output['error_info']['traceback'])
        self.assertTrue(output['error_info']['msg'])
        # no model objects should have been created
        self.assertEquals(model_count, PolicyModel.objects.all().count())
        
    def test_request_missing_key(self):
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_create')
        json_request = {
            'name': 'a_new_policy',  
            'source': 'policy:\n schedule:\n  True\n apply:\n  True',
            # Missing 'enabled' key.
        }
        rawjson = json.dumps(json_request)
        response = self.client.post(url, rawjson, content_type='application/json')
        output = json.loads(response.content)
        
        self.assertEquals(False, output['success'])
        self.assertEquals(False, output['error_info']['compile_error'])
        self.assertEquals('KeyError', output['error_info']['type'])
        self.assertEquals('', output['error_info']['traceback'])
        self.assertTrue(output['error_info']['msg'])
        # no model objects should have been created
        self.assertEquals(model_count, PolicyModel.objects.all().count())
        
        

class PolicyModify_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_policy']
    
    def test_basic(self):
        D = datetime.datetime
        now = datetime.datetime.now()
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_modify', 
                         kwargs={'id': 1} )
        json_request = {
            'name': 'another_policy',
            'source': 'policy:\n schedule:\n  True\n apply:\n  True',
            'enabled': True,
        }
        
        expected_output = {
            'success': True,
            'record': {
                'id': 1, 
                'name': 'another_policy', 
                'source': 'policy:\n schedule:\n  True\n apply:\n  True', 
                'enabled': True, 
                #'modified': timeutil.datetime_from_python(D(2010,1,4,hour=12)), 
                'last_run_time': timeutil.datetime_from_python(D(2010,1,4,hour=12)),
                },
            'error_info': {
                'compile_error': False, 
                'type': '', 
                'msg': '', 
                'traceback': '',
                },
            }
            
        self.assertNotEqual('another_policy', PolicyModel.objects.get(id=1).name)
        
        rawjson = json.dumps(json_request)
        response = self.client.post(url, rawjson, content_type='application/json')
        output = json.loads(response.content)
        
        modified = output['record'].pop('modified')
        self.assertEquals(expected_output, output)
        self.assertTrue(modified >= timeutil.datetime_from_python(now))
        self.assertEquals(model_count, PolicyModel.objects.all().count())
        self.assertEquals('another_policy', PolicyModel.objects.get(id=1).name)
        
    def test_nonexistent_id(self):
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_modify', 
                         kwargs={'id': model_count+1} )
        json_request = {
            'name': 'another_policy',
            'source': 'policy:\n schedule:\n  True\n apply:\n  True',
            'enabled': True,
        }
        
        rawjson = json.dumps(json_request)
        response = self.client.post(url, rawjson, content_type='application/json')
        output = json.loads(response.content)
        
        self.assertEquals(False, output['success'])
        self.assertEquals(False, output['error_info']['compile_error'])
        self.assertEquals('ObjectDoesNotExist', output['error_info']['type'])
        self.assertEquals('', output['error_info']['traceback'])
        self.assertTrue(output['error_info']['msg'])
        # no model objects should have been created
        self.assertEquals(model_count, PolicyModel.objects.all().count())
        
    def test_duplicate_name(self):
        # A policy with the given name already exists.  No new policy should be 
        # created.
        model_count = PolicyModel.objects.all().count()
        url = urlreverse('celerymanagementapp.dataviews.policy_modify', 
                         kwargs={'id': 2} )
        json_request = {
            'name': 'normal_policy',  # policy with this name already exists
            'source': 'policy:\n schedule:\n  True\n apply:\n  True',
            'enabled': True,
        }
        rawjson = json.dumps(json_request)
        response = self.client.post(url, rawjson, content_type='application/json')
        output = json.loads(response.content)
        
        self.assertEquals(False, output['success'])
        self.assertEquals(False, output['error_info']['compile_error'])
        self.assertEquals('DuplicateName', output['error_info']['type'])
        self.assertEquals('', output['error_info']['traceback'])
        self.assertTrue(output['error_info']['msg'])
        # no model objects should have been created
        self.assertEquals(model_count, PolicyModel.objects.all().count())
        












