from celery.events import EventReceiver, EventDispatcher
from celery.app import app_or_default

#==============================================================================#
CM_TASK_MODIFIED_EVENT = 'cm-task-modified'

#==============================================================================#
class Signal(object):
    """ Simple 'signal' class for dispatching and handling in-process events. 
    """
    def __init__(self, name=None):
        self.handlers = set()
        self.name = name
        
    def register(self, handler):
        self.handlers.add(handler)
        
    def unregister(self, handler):
        self.handlers.discard(handler)
        
    def __call__(self, *args, **kwargs):
        for handler in self.handlers:
            handler(*args, **kwargs)

on_task_modified = Signal('on_task_modified')
on_worker_started = Signal('on_worker_started')

#==============================================================================#
class Receiver(EventReceiver):
    def __init__(self, connection, logger, routing_key="#", app=None):
        self.logger = logger
        handlers = self._init_handlers()
        super(Receiver, self).__init__(connection, handlers, routing_key, app)
        
    def _init_handlers(self):
        handlers = {
            'worker-online': self.on_worker_online,
            CM_TASK_MODIFIED_EVENT: self.on_task_modified,
            }
        return handlers
    
    def on_worker_online(self, event):
        hostname = event.get('hostname')
        if hostname:
            self.logger.debug(
                'policy.signals.Receiver: Worker started: {0}'.format(hostname))
            on_worker_started(hostname)
    
    def on_task_modified(self, event):
        attrname = event.get('attrname')
        value = event.get('value')
        tasknames = event.get('tasknames')
        if tasknames and attrname and value:
            self.logger.debug(
                'policy.signals.Receiver: Task(s) modified: {0} {1} = {2}'
                .format(tasknames, attrname, value)
                )
            on_task_modified(tasknames, attrname, value)
        
class Dispatcher(EventDispatcher):
    def __init__(self, connection=None, app=None):
        app = app_or_default(app)
        connection = connection or app.broker_connection()
        super(Dispatcher, self).__init__(connection=connection, app=app)
        
    def close(self):
        super(Dispatcher, self).close()

#==============================================================================#

