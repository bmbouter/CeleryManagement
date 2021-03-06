import sys
import logging
from datetime import datetime, timedelta

from django.db import transaction

from celery.app import app_or_default
from celery.utils import instantiate, LOG_LEVELS
from celery.utils.timeutils import maybe_iso8601
from celery.task.control import inspect

from djcelery.snapshot import Camera as DjCeleryCamera

from celerymanagementapp.snapshot.state import State
from celerymanagementapp.models import DispatchedTask, RegisteredTaskType


REFRESH_REGISTERED_TASKS_EVERY = 60  #seconds
CLEAR_REGISTERED_TASKS_AFTER = 24*7  #hours


class Camera(DjCeleryCamera):
    TaskState = DispatchedTask
    
    def __init__(self, *args, **kwargs):
        super(Camera, self).__init__(*args, **kwargs)
        self.shutter_count = 0
        self.refresh_regtasks_every = REFRESH_REGISTERED_TASKS_EVERY
            
    def on_shutter(self, state):
        super(Camera, self).on_shutter(state)
        if (self.shutter_count % self.refresh_regtasks_every) == 0:
            self.refresh_registered_tasks()
        self.shutter_count += 1
        
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
        
    
    @transaction.commit_manually
    def refresh_registered_tasks(self):
        # Transactions are handled manually so all worker modifications appear 
        # to happen at once.  Otherwise, others could see the 
        # RegisteredTaskType models in an inconsistent state.
        i = inspect()
        workers = i.registered_tasks()
        # This if statement protects against the case when no workers are 
        # running.
        if workers:
            try:
                for workername, tasks in workers.iteritems():
                    RegisteredTaskType.clear_tasks(workername)
                    for taskname in tasks:
                        RegisteredTaskType.add_task(taskname, workername)
            except:
                transaction.rollback()
                pass
            else:
                transaction.commit()
                pass
        else:
            transaction.rollback()
                
    def on_cleanup(self):
        super(Camera, self).on_cleanup()
        self.clear_old_registered_tasks()
                
    def clear_old_registered_tasks(self):
        clrhrs = timedelta(hours=CLEAR_REGISTERED_TASKS_AFTER)
        cleartime = datetime.now() - clrhrs
        print 'cleartime: {0}'.format(cleartime)
        RegisteredTaskType.objects.filter(modified__lt=cleartime).delete()

    

# evcam function taken from celery.events.snapshot
def evcam(camera, freq=1.0, maxrate=None, loglevel=0,
        logfile=None, app=None, **kwargs):
    
    # Set process name that appears in logging messages.
    import multiprocessing
    multiprocessing.current_process().name = 'cm-event-handler'
    
    app = app_or_default(app)
    if not isinstance(loglevel, int):
        loglevel = LOG_LEVELS[loglevel.upper()]
    logger = app.log.setup_logger(loglevel=loglevel,
                                  logfile=logfile,
                                  name="cm.events")
    ##app.log.redirect_stdouts_to_logger(logger, loglevel=logging.INFO)
    logger.warning(
        "-> cmevents: Taking snapshots with %s (every %s secs.)" % (
            camera, freq))
    
    state = State()
    cam = instantiate(camera, state, app=app, freq=freq, maxrate=maxrate, 
                      logger=logger)
    cam.install()
    conn = app.broker_connection()
    recv = app.events.Receiver(conn, handlers={"*": state.event})
    try:
        try:
            recv.capture(limit=None)
        except (KeyboardInterrupt, SystemExit):
            pass
    finally:
        #import traceback
        #traceback.print_exc()
        cam.cancel()
        conn.close()
        logger.warning("-> cmevents: Shut down.\n")

