import time
import sys
from celery import states
from celery.events import state as celery_state

class DispatchedTask(celery_state.Task):
    # These fields in _disptask_defaults are added to those defined by 
    # celery.event.state.Task in _defaults.
    _disptask_defaults = {
        'waittime': None,
        }
        
    def __init__(self, **fields):
        if 'timestamp' in fields and not fields['timestamp']:
            fields['timestamp'] = time.time()
        super(DispatchedTask, self).__init__(**dict(self._disptask_defaults, 
                                                    **fields))
        ##print >> sys.stderr, 'DispatchedTask.__init__(): Creating DispatchedTask {0}'.format(self.uuid)
        
    def on_sent(self, timestamp=None, **fields):
        self.sent = timestamp
        if self.received:
            self.waittime = self.received - timestamp
        self.update(states.PENDING, timestamp, fields)

    def on_received(self, timestamp=None, **fields):
        self.received = timestamp
        if self.sent:
            self.waittime = timestamp - self.sent
        self.update(states.RECEIVED, timestamp, fields)


class State(celery_state.State):
    # Overwrite subclass version of this method so we can create DispatchedTasks
    def get_or_create_task(self, uuid):
        """Get or create task by uuid."""
        ##print >> sys.stderr, 'State.get_or_create_task(): retrieving DispatchedTask {0}'.format(uuid)
        try:
            return self.tasks[uuid]
        except KeyError:
            task = self.tasks[uuid] = DispatchedTask(uuid=uuid)
            return task

