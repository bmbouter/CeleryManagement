import itertools

from celery.task.control import broadcast as celery_broadcast
from celery.task.control import inspect as celery_inspect

from celerymanagementapp.policy import signals


DEFAULT_BROADCAST_TIMEOUT = 1
DEFAULT_INSPECT_TIMEOUT = 1

#==============================================================================#
def broadcast(*args, **kwargs):
    if 'timeout' not in kwargs:
        kwargs['timeout'] = DEFAULT_BROADCAST_TIMEOUT
    return celery_broadcast(*args, **kwargs)
    
def inspect(*args, **kwargs):
    if 'timeout' not in kwargs:
        kwargs['timeout'] = DEFAULT_INSPECT_TIMEOUT
    return celery_inspect(*args, **kwargs)


#==============================================================================#
def get_registered_tasks_for_worker(workername):
    i = inspect(timeout=1)
    tasks_by_worker = i.registered_tasks() or {}
    return tasks_by_worker.get(workername, [])
    
def get_registered_tasks(workernames=None):
    if isinstance(workernames, basestring):
        workernames = [workernames]
    i = inspect(destination=workernames, timeout=1)
    return i.registered_tasks() or {}
    
def get_all_registered_tasks():
    tasks_by_worker = get_registered_tasks()
    defined = set(x for x in 
                  itertools.chain.from_iterable(tasks_by_worker.itervalues()))
    return list(defined)
    
def get_all_worker_names():
    i = inspect(timeout=1)
    r = i.ping()
    if r:
        return r.keys()
    return []
    
#==============================================================================#
def _merge_broadcast_result(result):
    # merge a sequence of dicts into a single dict
    r = {}
    for dct in result:
        assert isinstance(dct, dict)
        r.update(dct)
    return r
    
def _condense_broadcast_result(result):
    checkval = None
    first_iteration = True
    for k, v in result.iteritems():
        if first_iteration:
            checkval = v
            first_iteration = False
        assert v==checkval, ('v!=checkval:\nv: {0}\ncheckval: {1}\n'
                             .format(v, checkval))
    return checkval

#==============================================================================#




