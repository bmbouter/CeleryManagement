from celery.events import EventReceiver

#==============================================================================#
class Signal(object):
    """ Simple 'signal' class for dispatching and handling in-process events. 
    """
    def __init__(self):
        self.handlers = set()
        
    def register(self, handler):
        self.handlers.add(handler)
        
    def unregister(self, handler):
        self.handlers.discard(handler)
        
    def __call__(self, *args, **kwargs):
        for handler in self.handlers:
            handler(*args, **kwargs)

on_task_modified = Signal()
on_worker_started = Signal()

#==============================================================================#
class Receiver(EventReceiver):
    def __init__(self, connection, logger, routing_key="#", node_id=None, app=None):
        self.logger = logger
        handlers = self._init_handlers()
        super(Receiver, self).__init__(connection, handlers, routing_key, 
                                       node_id, app)
        
    def _init_handlers(self):
        handlers = {
            'worker-online': self.on_worker_online,
            }
        return handlers
    
    def on_worker_online(self, event):
        hostname = event.get('hostname')
        if hostname:
            ##print 'policy.signals: Worker started: {0}'.format(hostname)
            self.logger.debug(
                'policy.signals.Receiver: Worker started: {0}'.format(hostname))
            on_worker_started(hostname)
        



