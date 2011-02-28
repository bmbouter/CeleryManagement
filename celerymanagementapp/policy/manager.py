import datetime
import time

from django.core.exceptions import ObjectDoesNotExist

from celerymanagementapp.models import PolicyModel
from celerymanagementapp.policy import policy, signals, util

#==============================================================================#
default_time = datetime.datetime(2000, 1, 1)

class Entry(object):
    """ An entry in the Policy registry. """
    
    def __init__(self, policy, modified, last_run_time=None):
        """ :param policy: A Policy object.
            :param modified: A datetime.datetime object which is the last time 
                the Policy was modified, or None.
            :param last_run_time: A datatime.datetime object which is the last 
                time the Policy was run, or None.
        """
        self.policy = policy
        self.last_run_time = last_run_time or default_time
        self.modified = modified  # this comes from PolicyModel.modified
        
    def is_due(self):
        """ :returns: A tuple: (bool, float).  The first field is whether the 
                      policy should be run now.  The second field is the number 
                      of seconds until the policy should be run *again*. 
        """
        return self.policy.is_due(self.last_run_time)
        
    def set_last_run_time(self, current_time):
        self.last_run_time = current_time
        
    def update(self, **kwargs):
        """ Updates the entry's values.  The fields are given as keyword 
            arguments.  Any fields not explicitly stated will not be changed. 
        """
        self.policy = kwargs.pop('policy', self.policy)
        self.last_run_time = kwargs.pop('last_run_time', self.last_run_time)
        self.modified = kwargs.pop('modified', self.modified)


#==============================================================================#
class Registry(object):
    """ The collection of enabled Policies within the system. """
    def __init__(self, logger):
        self.logger = logger
        self.data = {}
        self.refresh()
        
        msg = 'Found the following policies:\n    '
        if self.data:
            msg += '\n    '.join(e.policy.name for e in self.data.itervalues())
        else:
            msg += '(No policies found.)'
        self.logger.info(msg)
        
    def __iter__(self):
        return self.data.itervalues()
        
    def register(self, obj):
        """ Register a PolicyModel object that is not currently in the 
            Registry.
            
            :param obj: A PolicyModel instance.
        """
        assert obj.enabled
        assert obj.id not in self.data
        policyobj = policy.Policy(source=obj.source, id=obj.id, name=obj.name)
        entry = Entry(policy=policyobj, modified=obj.modified, 
                      last_run_time=obj.last_run_time)
        self.data[obj.id] = entry
        
    def reregister(self, obj):
        """ Update the information of a PolicyModel that has been modified. 
            
            :param obj: A PolicyModel instance.
        """
        assert obj.enabled
        entry = self.data[obj.id]
        assert (obj.last_run_time is None or 
                obj.last_run_time <= entry.last_run_time)
        entry.policy.reinit(source=obj.source, name=obj.name)
        entry.update(modified=obj.modified)
        
    def unregister(self, id):
        """ Remove a PolicyModel--it was already deleted from the database. 
        
            :param id: The PolicyModel id in the database.
        """
        del self.data[id]
        
    def refresh(self):
        """ Examine the PolicyModel objects in the database looking for changes. 
        
            Newly-enabled Policies are registered, newly-disabled Policies are 
            unregistered, and enabled Policies with other changes are 
            reregistered.
        """
        updated = False
        objects = PolicyModel.objects.all()
        for id, entry in self.data.iteritems():
            try:
                obj = objects.get(id=id)
                # existing enabled Policy was modified
                if obj.enabled and obj.modified > entry.modified:
                    self.reregister(obj)
                    updated = True
                # existing enabled Policy was disabled
                elif not obj.enabled:
                    self.unregister(id)
                    updated = True
            except ObjectDoesNotExist:
                # existing enabled Policy was deleted
                self.unregister(id)
                updated = True
        
        for obj in objects:
            # disabled (or new) Policy was enabled
            if obj.enabled and obj.id not in self.data:
                self.register(obj)
                updated = True
        
        return updated
        
    def save(self, id, current_time):
        """ Save the Policy with the given id to the database. """
        entry = self.data[id]
        obj = PolicyModel.objects.get(id=id)
        if obj.modified > entry.modified:
            self.reregister(obj)
        obj.last_run_time = entry.last_run_time
        ##obj.modified, entry.modified = current_time, current_time
        obj.save()
        
    def close(self):
        self.refresh()
        

#==============================================================================#
_setting_names = ('ignore_result', 'routing_key', 'exchange', 
                  'default_retry_delay', 'rate_limit', 
                  'store_errors_even_if_ignored', 'acks_late', 'expires',
                 )
    
def get_task_settings(workername, tasknames):
    """ Get the settings for one or more tasks. 
    
        :param workername: The name of a worker to get the task settings from, 
                           or None to examine all task settings.
        :param tasknames: The name or names of tasks to get settings from.  It 
                          can either be a single string, a or a tuple or list 
                          of strings.
        :returns: A dict whose format varies depending on whether a workername 
                  is supplied or not. If the workername is None, the dict has 
                  three levels: name of the worker, name of the task, name of 
                  the setting, and finally the setting's value. If a workername 
                  is supplied, the top level of the dict is omitted.
    """
    destination = [workername] if workername else None
    settings = util.broadcast('get_task_settings', destination=destination, 
                         arguments={'tasknames': tasknames, 
                         'setting_names': _setting_names}, reply=True)
    settings = util._merge_broadcast_result(settings)
    if workername:
        return settings.get(workername)
    else:
        return settings
    
def get_all_task_settings():
    """ Like get_task_settings(), but it always returns the settings for all 
        tasks in all workers. 
    """
    # don't do anything if there are no workers
    if len(util.get_all_worker_names()) == 0:
        return {}
    settings = util.broadcast('get_task_settings', 
                         arguments={'tasknames': None, 
                         'setting_names': _setting_names}, 
                         reply=True)
    settings = util._merge_broadcast_result(settings)
    return util._condense_broadcast_result(settings) or {}
    
def update_tasks_settings(workername, tasks_settings):
    """ Update settings for one or more tasks in the given worker or all 
        workers. 
        
        The tasks_settings argument must be a dict with the following format: 
        dict[taskname][settingname] = settingvalue.  For example::
        
            {
                'tasks.task1': {
                    'ignore_result': False,
                    'routing_key': 'MyRoutingKey',
                },
                'tasks.task2': {
                    'acks_late': True,
                },
            }
    """
    util.broadcast('update_tasks_settings', destination=[workername],
              arguments={'tasks_settings': tasks_settings})

def restore_task_settings(restore_data):
    """ Restores task settings to the given values.  This restores the initial 
        task settings when the Task Manager is closed. 
        
        The restore_data argument must be a dict.  The keys correspond to task 
        names, and the values are tuples containing: 1. a dict mapping setting 
        names to their new values, and 2. a list of setting names to erase.  
        Every setting name should be found in one or the other, but not both.
        Here is a brief example (for brevity, not all setting names are shown)::
            
            {
                'task.task1': (
                    {
                        'ignore_result': True,
                    },
                    ['expires', acks_late],
                ),
                'task.task2': (
                    {
                        'exchange': 'MyExchange',
                        'routing_key': 'MyRoutingKey',
                    },
                    ['expires', 'rate_limit'],
                ),
            }
    """
    # only broadcast if there are workers
    if len(util.get_all_worker_names()):
        util.broadcast('restore_task_settings', 
                  arguments={'restore_data': restore_data})


class TaskSettings(object):
    """ The current and initial settings for a Task.  See TaskSettingsManager 
        for more information.
    """
    def __init__(self, task_name, initial_settings):
        self.name = task_name
        self.initial_settings = initial_settings.copy()
        self.settings = {}
        
    def restore(self):
        """ Restore the Task to its original settings. """
        # restore Task settings to the original settings
        restore = dict((k, v) for (k, v) in self.initial_settings.iteritems() 
                                         if self.settings.get(k, v) != v)
        # TODO: maybe base the restore behavior here on _setting_names in 
        # additon to self.settings
        erase = [k for k in self.settings if k not in self.initial_settings]
        return restore, erase
        
    def set(self, attr, value):
        # a setting on a Task was changed
        self.settings[attr] = value
    
    def current(self):
        # get current settings, for instance, for writing settings of 
        # newly-started worker
        return self.settings
        

class TaskSettingsManager(object):
    """ Maintains the Task class settings inforamtion.

        When workers start up, their Task classes are updated with the current 
        settings so that Tasks are consistent across a cluster.  When the 
        policy-manager shuts down, Task classes are restored to their initial 
        settings. 
    """
    def __init__(self, logger):
        self.logger = logger
        self.data = {}
        signals.on_task_modified.register(self.on_tasks_modified)
        signals.on_worker_started.register(self.on_worker_start)
        self._initialize_settings()
        
    def cleanup(self):
        """ Clean up resources owned by the settings manager.  This must be 
            called. 
        """
        signals.on_worker_started.unregister(self.on_worker_start)
        signals.on_task_modified.unregister(self.on_tasks_modified)
        self.restore()
        
    def _initialize_settings(self):
        """ Initialize settings based on known tasks and workers. """
        tasks_settings = get_all_task_settings()
        
        found_tasks = self._store_settings_info(tasks_settings)
        if found_tasks:
            msg = 'Found existing tasks:\n    '
            msg += '\n    '.join(found_tasks)
            self.logger.info(msg)
        else:
            msg = 'No existing tasks found.  Is celeryd running?'
            self.logger.warn(msg)
            
    def _store_settings_info(self, tasks_settings):
        """ Store a task's current settings. """
        # verify that task_settings is a dict
        # return list of tasks found
        if not isinstance(tasks_settings, dict):
            self.logger.error(
                'Error retrieving task settings: {0}\n'.format(tasks_settings) +
                'This may indicate a worker is not properly configured for use with\n' +
                'CeleryManagement.  Please check that the celeryconfig.py (and/or settings.py\n' + 
                'for django-celery) contains the CeleryManagement imports in the CELERY_IMPORTS\n' + 
                'setting. '
                )
            return
        found_tasks = []
        for taskname, tasksettings in tasks_settings.iteritems():
            if taskname=='error' or not isinstance(tasksettings, dict):
                self.logger.error(
                    'Error reading task settings: {0}'.format(tasksettings))
                continue
            self.logger.debug(
                'Found task settings -> {0}:\n    {1}'.format(
                    taskname, 
                    '\n    '.join('{0}: {1}'.format(k, v) 
                                  for k, v in tasksettings.iteritems())
                )
            )
            ts = TaskSettings(taskname, tasksettings)
            found_tasks.append(taskname)
            self.data[taskname] = ts
        return found_tasks
        
    def on_tasks_modified(self, tasknames, setting_name, value):
        """ Handles the task modified event so that Task class settings can be 
            updated accordingly. 
        """
        self.logger.debug(
            'Tasks modified:: {0}: {1} = {2}'.format(
                ','.join(tasknames), setting_name, value)
            )
        for taskname in tasknames:
            if taskname in self.data:
                self.data[taskname].set(setting_name, value)
                
    def on_worker_start(self, workername):
        """ Handles the worker started event so that they can be given the 
            current Task class settings. 
        """
        tasknames = util.get_registered_tasks_for_worker(workername)  # TODO
        tasks_settings = dict( (taskname, self.data[taskname].current()) 
                               for taskname in tasknames 
                                   if taskname in self.data)
        # { taskname: { setting_name: value, ...}, ... }
        update_tasks_settings(workername, tasks_settings)
        new_tasknames = [s for s in tasknames if s not in self.data]
        new_task_settings = get_task_settings(workername, new_tasknames)
        found_tasks = self._store_settings_info(new_task_settings)
        msg =  'Worker "{0}" has started.\n'
        msg += 'Found the following tasks:\n    '.format(workername)
        msg += '\n    '.join((name + ('*' if name in new_tasknames else '')) 
                             for name in tasknames)
        self.logger.info(msg)
                    
    def restore(self):
        """ Restores the Task classes' initial settings.  This is used when the 
            policy-manager shuts down. 
        """
        restore_data = {}
        for taskname, settings in self.data.iteritems():
            restore, erase = settings.restore()
            restore_data[taskname] = (restore, erase)
        msg = 'Restoring settings for the following tasks:\n    '
        if restore_data:
            msg += '\n    '.join(restore_data.iterkeys())
        else:
            msg += '(No tasks found.)'
        self.logger.info(msg)
        restore_task_settings(restore_data)
            
        
        
#==============================================================================#

def create_policy(name, source=None, schedule_src=None, condition_srcs=None, 
                  apply_src=None, enabled=True):
    """ Creates a new policy model object to the database.  If it doesn't 
        compile, an exception will be thrown.
    """
    assert isinstance(name, basestring)  # TODO: make this an exception
    source = policy.combine_sources(source, schedule_src, condition_srcs, 
                                    apply_src)
    # The following method should throw an exception if it fails, so the 
    # following 'raise' statement should never get called.  It is here for 
    # explanatory purposes.
    if not policy.check_source(source):
        msg = 'Invariant error:  policy.check_source() returned False.'
        raise RuntimeError(msg)
    model = PolicyModel(name=name, source=source, enabled=enabled)
    model.modified = datetime.datetime.now()
    model.save()
    return model
    
def save_policy(model):
    """ Saves an existing policy model to the database.  If it doesn't compile, 
        an excecption will be thrown.
    """
    # The following should throw an exception if it fails.
    if not policy.check_source(model.source):
        msg = 'Invariant error:  policy.check_source() returned False.'
        raise RuntimeError(msg)
    model.modified = datetime.datetime.now()
    model.save()
    
#==============================================================================#
    
    

