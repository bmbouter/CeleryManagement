import sys
from datetime import datetime, timedelta

from celery.app import app_or_default
from celery.utils import instantiate, LOG_LEVELS
from celery.utils.timeutils import maybe_iso8601

from djcelery.snapshot import Camera as DjCeleryCamera

from celerymanagementapp.snapshot.state import State
from celerymanagementapp.models import DispatchedTask

class Camera(DjCeleryCamera):
    TaskState = DispatchedTask
    
    def __init__(self, *args, **kwargs):
        ##print >> sys.stderr, 'Camera.__init__(): creating celerymanagementapp.Camera'
        super(Camera, self).__init__(*args, **kwargs)
        
    def on_shutter(self, state):
        ##print >> sys.stderr, 'Camera.on_shutter(): shutter triggered'
        super(Camera, self).on_shutter(state)
                
    def handle_task(self, (uuid, task), worker=None):
        if task.worker and task.worker.hostname:
            worker = self.handle_worker((task.worker.hostname, task.worker))
        #import pdb; pdb.set_trace()
        defaults = {
            "name":     task.name,
            "state":    task.state,

            "worker":   worker,

            "runtime":  task.runtime,
            "waittime": task.waittime,
            "totaltime": task.totaltime,

            "tstamp":   datetime.fromtimestamp(task.timestamp),
            "sent":     task.sent and datetime.fromtimestamp(task.sent),
            "received": task.received and datetime.fromtimestamp(task.received),
            "started":  task.started and datetime.fromtimestamp(task.started),
            "succeeded": task.succeeded and datetime.fromtimestamp(task.succeeded),
            "failed":   task.failed and datetime.fromtimestamp(task.failed),

            "expires":  maybe_iso8601(task.expires),
            "result":   task.result or task.exception,
            "retries":  task.retries,
            "eta":      maybe_iso8601(task.eta),
            }
        return self.update_task(task.state, task_id=uuid, defaults=defaults)
                          

    

# evcam function taken from celery.events.snapshot
def evcam(camera, freq=1.0, maxrate=None, loglevel=0,
        logfile=None, app=None):
    ##print >> sys.stderr, 'evcam()...'
    app = app_or_default(app)
    if not isinstance(loglevel, int):
        loglevel = LOG_LEVELS[loglevel.upper()]
    logger = app.log.setup_logger(loglevel=loglevel,
                                  logfile=logfile,
                                  name="celery.evcam")
    logger.info(
        "-> cmevcam: Taking snapshots with %s (every %s secs.)\n" % (
            camera, freq))
    
    ##print >> sys.stderr, 'evcam: creating state'
    state = State()
    cam = instantiate(camera, state, app=app,
                      freq=freq, maxrate=maxrate, logger=logger)
    cam.install()
    conn = app.broker_connection()
    ##print >> sys.stderr, 'evcam: creating event receiver'
    recv = app.events.Receiver(conn, handlers={"*": state.event})
    try:
        try:
            ##print >> sys.stderr, 'evcam: capturing events'
            recv.capture(limit=None)
        except KeyboardInterrupt:
            raise SystemExit
    finally:
        ##print >> sys.stderr, 'exc_info: {0}'.format(sys.exc_info())
        import traceback
        traceback.print_exc()
        ##print >> sys.stderr, 'evcam: cleaning up'
        cam.cancel()
        conn.close()

