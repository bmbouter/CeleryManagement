import json
import os

from celery.decorators import task

from celerymanagementapp.taskcontrol import demo_dispatch

@task(ignore_result=True)
def launch_demotasks(dispatchid, tmpfilename):
    try:
        f = open(tmpfilename, 'rb')
    except IOError as e:
        msg =  'An error occurred while trying to open the tmpfile:\n'
        if e.filename:
            msg += '{0}: {1}'.format(e.strerror, e.filename)
        else:
            msg += '{0}'.format(e.strerror)
        print msg
        raise
    
    rawjson = f.read()
    f.close()
    os.remove(tmpfilename)
    
    jsondata = json.loads(rawjson)
    
    taskname = jsondata['name']
    args = jsondata.get('args', [])
    kwargs = jsondata.get('kwargs', {})
    options = jsondata.get('options', {})
    rate = jsondata['rate']
    runfor = jsondata['runfor']
    
    demo_dispatch(taskname, dispatchid, runfor, rate, options, args, kwargs)


