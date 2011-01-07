import json
import uuid

#from celery.decorators import task
from celery.task import Task
from celerymanagementapp.taskcontrol import demo_dispatch
from celerymanagementapp import jsonutil


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


