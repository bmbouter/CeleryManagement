import datetime
import time

from django.core.exceptions import ObjectDoesNotExist

from celery.task.control import broadcast, inspect

from celerymanagementapp.models import PolicyModel
from celerymanagementapp.policy import policy, signals

#==============================================================================#
default_time = datetime.datetime(2000,1,1)

class Entry(object):
    def __init__(self, policy, modified, last_run_time=None):
        self.policy = policy
        self.last_run_time = last_run_time or default_time
        self.modified = modified
        
    def is_due(self):
        return self.policy.is_due(self.last_run_time)
        
    def set_last_run_time(self, current_time):
        self.last_run_time = current_time
        
    def update(self, **kwargs):
        self.policy = kwargs.pop('policy', self.policy)
        self.last_run_time = kwargs.pop('last_run_time', self.last_run_time)
        self.modified = kwargs.pop('modified', self.modified)


#==============================================================================#
class Registry(object):
    def __init__(self):
        self.data = {}
        
    def __iter__(self):
        return self.data.itervalues()
        
    def register(self, obj):
        assert obj.enabled
        assert obj.id not in self.data
        policyobj = policy.Policy(source=obj.source, id=obj.id, name=obj.name)
        entry = Entry(policy=policyobj, modified=obj.modified, last_run_time=obj.last_run_time)
        self.data[obj.id] = entry
        
    def reregister(self, obj):
        assert obj.enabled
        entry = self.data[obj.id]
        assert obj.last_run_time is None or obj.last_run_time <= entry.last_run_time
        entry.policy.reinit(source=obj.source, name=obj.name)
        entry.update(modified=obj.modified)
        
    def unregister(self, id):
        del self.data[id]
        
    def refresh(self):
        updated = False
        objects = PolicyModel.objects.all()
        for id,entry in self.data.iteritems():
            try:
                obj = objects.get(id=id)
                if obj.enabled and obj.modified > entry.modified:
                    self.reregister(obj)
                    updated = True
                elif not obj.enabled:
                    self.unregister(id)
                    updated = True
            except ObjectDoesNotExist:
                self.unregister(id)
                updated = True
        
        for obj in objects:
            if obj.enabled and obj.id not in self.data:
                self.register(obj)
                updated = True
        
        return updated
                
    def save(self, id, current_time):
        entry = self.data[id]
        obj = PolicyModel.objects.get(id=id)
        if obj.modified > entry.modified:
            self.reregister(obj)
        obj.last_run_time = entry.last_run_time
        obj.modified, entry.modified = current_time, current_time
        obj.save()
        
    def close(self):
        self.refresh()
        

#==============================================================================#
def get_registered_tasks(workername):
    i = inspect()
    tasks_by_worker = i.registered_tasks() or {}
    return tasks_by_worker.get(workername, [])
    
def _merge_broadcast_result(result):
    r = {}
    for x in result:
        assert isinstance(x, dict)
        r.update(x)
    return r
    
def _condense_broadcast_result(result):
    checkval = None
    first_iteration = True
    for k,v in result.iteritems():
        if first_iteration:
            checkval = v
            first_iteration = False
        assert v==checkval, 'v!=checkval:\nv: {0}\ncheckval: {1}\n'.format(v,checkval)
    return checkval
    
_setting_names = ('ignore_result', 'routing_key', 'exchange', 
                  'default_retry_delay', 'rate_limit', 
                  'store_errors_even_if_ignored', 'acks_late', 'expires',
                 )
    
def get_task_settings(workername, tasknames):
    destination = [workername] if workername else None
    settings = broadcast('get_task_settings', destination=destination, 
                         arguments={'tasknames': tasknames, 
                         'setting_names': _setting_names}, reply=True)
    settings = _merge_broadcast_result(settings)
    #print 'settings: {0}'.format(settings)
    if workername:
        return settings.get(workername)
    else:
        return settings
    
def get_all_task_settings():
    settings = broadcast('get_all_task_settings', 
                         arguments={'setting_names': _setting_names}, 
                         reply=True)
    settings = _merge_broadcast_result(settings)
    return _condense_broadcast_result(settings) or {}
    
def update_tasks_settings(workername, tasks_settings):
        broadcast('update_tasks_settings', destination=[workername],
                  arguments={'tasks_settings': tasks_settings})

def restore_task_settings(restore_data):
        broadcast('restore_task_settings', 
                  arguments={'restore_data': restore_data})



class TaskSettings(object):
    def __init__(self, task_name, initial_settings):
        self.name = task_name
        self.initial_settings = initial_settings.copy()
        self.settings = {}
        
    def restore(self):
        # restore Task settings to the original settings
        restore = dict((k,v) for (k,v) in self.initial_settings.iteritems() 
                                       if self.settings.get(k,v) != v)
        erase = [k for k in self.settings if k not in self.initial_settings]
        return restore, erase
        
    def set(self, attr, value):
        # a setting on a Task was changed
        self.settings[attr] = value
    
    def current(self):
        # get current settings, for instance, for writing settings of newly-started worker
        return self.settings
        

class TaskSettingsManager(object):
    def __init__(self):
        self.data = {}
        signals.on_task_modified.register(self.on_tasks_modified)
        signals.on_worker_started.register(self.on_worker_start)
        # TODO: get data from existing workers
        self._initialize_settings()
        
    def cleanup(self):
        signals.on_worker_started.unregister(self.on_worker_start)
        signals.on_task_modified.unregister(self.on_tasks_modified)
        self.restore()
        
    def _initialize_settings(self):
        settings = get_all_task_settings()
        for taskname, tasksettings in settings.iteritems():
            if taskname=='error':
                print 'cmrun: ERROR: {0}'.format(tasksettings)
            print 'cmrun: Found existing task: {0}'.format(taskname)
            ts = TaskSettings(taskname, settings)
            self.data[taskname] = ts
        
    def on_tasks_modified(self, tasknames, setting_name, value):
        for taskname in tasknames:
            if taskname in self.data:
                self.data[taskname].set(setting_name, value)
                
    def on_worker_start(self, workername):
        tasknames = get_registered_tasks(workername)  # TODO
        tasks_settings = dict( (taskname, self.data[taskname].current()) 
                               for taskname in tasknames 
                                   if taskname in self.data)
        # { taskname: { setting_name: value, ...}, ... }
        update_tasks_settings(workername, tasks_settings)
        new_tasknames = [s for s in tasknames if s not in self.data]
        new_task_settings = get_task_settings(workername, new_tasknames)
        for taskname,settings in new_task_settings.iteritems():
            ts = TaskSettings(taskname, settings)
            self.data[taskname] = ts
                    
    def restore(self):
        restore_data = {}
        for taskname,settings in self.data.iteritems():
            restore,erase = settings.restore()
            restore_data[taskname] = (restore, erase)
        restore_task_settings(restore_data)
            
        
        
#==============================================================================#

def create_policy(name, source=None, schedule_src=None, condition_srcs=None, apply_src=None, enabled=True):
    """ Creates a new policy model object to the database.  If it doesn't 
        compile, an exception will be thrown.
    """
    assert isinstance(name, basestring)  # TODO: make this an exception
    source = policy.combine_sources(source, schedule_src, condition_srcs, apply_src)
    # The following should throw an exception if it fails.
    if not policy.check_source(source):
        raise RuntimeError('Invariant error:  policy.check_source() returned False.')
    model = PolicyModel(name=name, source=source, enabled=enabled)
    model.save()
    return model
    
def save_policy(model):
    """ Saves an existing policy model to the database.  If it doesn't compile, 
        an excecption will be thrown.
    """
    # The following should throw an exception if it fails.
    if not policy.check_source(model.source):
        raise RuntimeError('Invariant error:  policy.check_source() returned False.')
    model.save()
    
#==============================================================================#
    
    

