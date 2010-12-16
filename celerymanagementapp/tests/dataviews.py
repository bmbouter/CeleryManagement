import json

from django.core.urlresolvers import reverse as urlreverse
from django.test.client import Client

from celerymanagementapp.tests import base, testcase_settings
from celerymanagementapp.models import OutOfBandWorkerNode


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
    #    self.client = Client()
        self.outofbandworker_url = '/celerymanagementapp/outofbandworker/'

    def test_create_outofbandworker(self):
        f = open(testcase_settings.OUTOFBANDWORKER_SSH_KEY_FILE) #path to ssh_key file for testing
        response = self.client.post(self.outofbandworker_url, {
                        'ip' : testcase_settings.OUTOFBANDWORKER_IP,
                        'username' : testcase_settings.OUTOFBANDWORKER_USERNAME,
                        'ssh_key' : f,
                        'celeryd_start_cmd' : testcase_settings.OUTOFBANDWORKER_CELERYD_START ,
                        'celeryd_stop_cmd' : testcase_settings.OUTOFBANDWORKER_CELERYD_START,
                        'celeryd_status_cmd' : testcase_settings.OUTOFBANDWORKER_CELERYD_START
                            })
        f.close()
        self.assertEquals(repsonse.status_code, 200)
        outofbandworkers = OutOfBandWorkerNode.objects.all()
        self.assertEquals(len(outofbandworkers), 1)


# class WorkerSubprocessesDataview_TestCase(base.CeleryManagement_DBTestCaseBase):
    # pass
        
# class PendingTaskCountDataview_TestCase(base.CeleryManagement_DBTestCaseBase):
    # pass
        
# class TasksPerWorkerDataview_TestCase(base.CeleryManagement_DBTestCaseBase):
    # pass

