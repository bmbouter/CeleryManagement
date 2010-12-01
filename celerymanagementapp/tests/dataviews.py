import json

from django.core.urlresolvers import reverse as urlreverse

from celerymanagementapp.tests import base


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
                [u'task1', {'runtime': {'average': 2.6} }],
                [u'task2', {'runtime': {'average': 2.5} }],
                ]
            }
        rawjson = json.dumps(json_request)
        response = self.client.post(url, rawjson, content_type='application/json')
        output = json.loads(response.content)
        
        self.assertEquals(expected_output, output)
        
        


