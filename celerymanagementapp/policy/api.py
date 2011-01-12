import datetime
import itertools

from celerymanagementapp.policy import exceptions, signals

#==============================================================================#
class ApiError(exceptions.Error):
    clsname = PolicyApiError

class TimeIntervalError(exceptions.Error):
    clsname = 'PolicyTimeIntervalError'


#==============================================================================#
def make_time_interval(arg):
    now = datetime.datetime.now()
    if isinstance(arg, datetime.timedelta):
        result = (now-arg, now)
    elif isinstance(arg, (tuple, list)):
        if len(arg) != 2:
            msg = 'Sequence arguments must have a length of two.'
            raise TimeIntervalError(msg)
        a,b = arg
        if isinstance(a, datetime.timedelta):
            if isinstance(b, datetime.timedelta):
            # (timedelta 'a' before now,  timedelta 'b' before now)
                result = (now-a, now-b)
            else:
            # (timedelta 'a' before time 'b',  time 'b')
                result = (b-a, b)
        elif isinstance(b, datetime.timedelta):
            # (time 'a',  timedelta 'b' after time 'a')
            result = (a, a+b)
        else:
            # (time 'a', time'b')
            result = arg
    else:
        msg = 'Argument must be a datetime.timedelta or a sequence of length two.'
        raise TimeIntervalError(msg)
    return (min(result), max(result))

def string_or_sequence(arg):
    if isinstance(arg, basestring):
        arg = [arg]
    return arg
    
def get_filter_seq_arg(field, arg):
    if arg:
        if isinstance(arg, (list, tuple)):
            return { '{0}__in'.format(field): arg }
        else:
            return { field: arg }
    return {}
    
def filter(interval=None, workers=None, tasks=None):
    filterargs = {}
    if interval is not None:
        interval = make_time_interval(interval)
        filterargs['senttime__gte'] = interval[0]
        filterargs['senttime__lt'] = interval[1]
    filterargs.update(get_filter_seq_arg('worker', workers))
    filterargs.update(get_filter_seq_arg('taskname', tasks))
    qs = Model.objects.filter(**filterargs)
    
    
    
    if workers:
        if isinstance(workers, (list, tuple)):
            q = {'?__in': workers}
        else:
            q = {'?': workers}
            
#==============================================================================#
def get_all_registered_tasks():
    i = inspect()
    tasks_by_worker = i.registered_tasks() or {}
    
    i = inspect()
    tasks_by_worker = i.registered_tasks() or {}
    defined = set(x for x in 
                  itertools.chain.from_iterable(workers.itervalues()))
    defined = list(defined)
    defined.sort()
    return defined
    
def _merge_broadcast_result(result):
    r = {}
    for x in result:
        if isinstance(x, dict):
            r.update(x)
    return r


#==============================================================================#
class ItemApi(object):
    def __init__(self, names=None):
        self.names = names or []

class ItemsCollectionApi(object):
    ItemApi = None
    def __init__(self):
        pass
    def __getitem__(self, names):
        if isinstance(names, basestring):
            names = (names,)
        return self.ItemApi(names)
        
    def all(self):
        return self.ItemApi(None)

#==============================================================================#
class TaskSettingBase(object):
    def signal_modified(self, tasks, value):
        signals.on_task_modified(tasknames, self.setting_name, value)

class TaskApi(ItemApi):
    def __init__(self, names=None):
        if not names:
            names = get_all_task_names()
        super(TaskApi, self).__init__(names)
        
    def _setting_modified(self, setting_name, value):
        # Call this when a setting has been successfully modified by a TaskApi method.
        signals.on_task_modified(self.names, setting_name, value)
        
    def get_ignore_result(self):
        if len(self.names) != 1:
            raise ApiError('Cannot retrieve this attribute for multiple tasks.')
        r = broadcast('get_task_attribute', arguments={'taskname': self.names[0], 'attrname': 'ignore_result'}, reply=True)
        r = _merge_broadcast_result(r)
        if not r:
            raise ApiError('Unable to retrieve task attribute {0}.'.format('ignore_result'))
        # check that all 'values' are equal
        after_first = False
        checkval = None
        for val in r.itervalues():
            if not after_first:
                checkval = val
                after_first = True
            if val != checkval:
                raise ApiError('Task attribute {0} is not consistent.'.format('ignore_result'))
        # check that the value doesn't indicate an error
        if isinstance(checkval, dict) and 'error' in checkval:
            raise ApiError('Error occurred while retrieving task attribute {0}.'.format('ignore_result'))
        return checkval
        
    def set_ignore_result(self, val):
        r = broadcast('set_task_attribute', arguments={'tasknames': self.names, 'attrname':'ignore_result', 'value': val}, reply=True)
        r = _merge_broadcast_result(r)
        if not r:
            raise ApiError('Unable to set task attribute {0}.'.format('ignore_result'))
        # check that all 'values' are equal
        after_first = False
        checkval = None
        for val in r.itervalues():
            if not after_first:
                checkval = val
                after_first = True
            if val != checkval:
                raise ApiError('Task attribute {0} is not consistent.'.format('ignore_result'))
        # check that the value doesn't indicate an error
        if isinstance(checkval, dict) and 'error' in checkval:
            raise ApiError('Error occurred while setting task attribute {0}.'.format('ignore_result'))
        self._setting_modified('ignore_result', checkval)
        
    ignore_result = property(get_ignore_result, set_ignore_result)
    
class TasksCollectionApi(ItemsCollectionApi):
    ItemApi = TaskApi
    
#==============================================================================#
class WorkerApi(ItemApi):
    def __init__(self, names=None):
        if not names:
            names = get_all_worker_names()
        super(WorkerApi, self).__init__(names)
    
class WorkersCollectionApi(ItemsCollectionApi):
    ItemApi = WorkerApi

#==============================================================================#






