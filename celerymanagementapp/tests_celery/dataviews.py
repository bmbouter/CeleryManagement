import json

from django.core.urlresolvers import reverse as urlreverse
from celerymanagementapp.tests_celery import base


class WorkerSubprocessesDataview_TestCase(base.CeleryManagement_DBTestCaseBase):
    use_default_procs = True
    def test_basic(self):
        url = urlreverse('celerymanagementapp.dataviews.worker_subprocesses_dataview', kwargs={'name':'all'})
        
        response = self.client.get(url)
        output = json.loads(response.content)
        
        self.assertTrue(len(output) > 0)
        self.assertTrue(all(isinstance(x,int) for x in output.itervalues()))
        

class PendingTaskCountDataview_TestCase(base.CeleryManagement_DBTestCaseBase):
    use_default_procs = True
    def test_basic(self):
        url = urlreverse('celerymanagementapp.dataviews.pending_task_count_dataview', kwargs={'name':'all'})
        
        response = self.client.get(url)
        output = json.loads(response.content)
        
        self.assertTrue(len(output) > 0)
        self.assertTrue(all(isinstance(x,int) for x in output.itervalues()))
        
class TasksPerWorkerDataview_TestCase(base.CeleryManagement_DBTestCaseBase):
    use_default_procs = True
    def test_basic(self):
        url = urlreverse('celerymanagementapp.dataviews.tasks_per_worker_dataview', kwargs={'name':'all'})
        
        response = self.client.get(url)
        output = json.loads(response.content)
        
        self.assertTrue(len(output) > 0)
        vals = []
        for task,workers in output.iteritems():
            vals.extend([x for x in workers.itervalues()])
        self.assertTrue(all(isinstance(x,int) for x in vals))



