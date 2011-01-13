import json
import uuid

#from celery.decorators import task
from celery.task import Task
from celerymanagementapp.taskcontrol import demo_dispatch
from celerymanagementapp import jsonutil
from celerymanagementapp.models import InBandWorkerNode


class launch_demotasks(Task):
    ignore_result = True
    
    def run(self, rawjson):    
        jsondata = jsonutil.loads(rawjson)
        dispatchid = uuid.UUID(self.request.id).hex
        
        taskname = jsondata['name']
        args = jsondata.get('args', [])
        kwargs = jsondata.get('kwargs', {})
        options = jsondata.get('options', {})
        rate = jsondata['rate']
        runfor = jsondata['runfor']
        
        demo_dispatch(taskname, dispatchid, runfor, rate, options, args, kwargs)
        


# @task(ignore_result=True)
# def launch_demotasks(rawjson):
    # jsondata = jsonutil.loads(rawjson)
    
    # taskname = jsondata['name']
    # args = jsondata.get('args', [])
    # kwargs = jsondata.get('kwargs', {})
    # options = jsondata.get('options', {})
    # rate = jsondata['rate']
    # runfor = jsondata['runfor']
    
    # demo_dispatch(taskname, dispatchid, runfor, rate, options, args, kwargs)

class start_celeyrd_on_vm(Task):
    default_retry_delay = 30 # retry every 30 seconds
    max_retries = 20  # wait a total of 10 minutes
    ignore_result = True
    
    def run(self, in_band_worker_node_pk):
        print 'Running start_celeryd_on_vm(%s)' % in_band_worker_node_pk
        node = InBandWorkerNode.objects.get(pk=in_band_worker_node_pk)
        if not node.is_celeryd_running():
            print 'I should start celeryd now'
            output = node.celeryd_start()
            print 'output = %s' % output
            self.retry()
