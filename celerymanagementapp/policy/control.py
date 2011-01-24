if 0:
    from celery.worker.control import Panel
    from celery.registry import tasks as tasks_registry
    from celery.task.base import BaseTask

    #==============================================================================#
    def _get_task_class(name):
        try:
            task = tasks_registry[name]
        except tasks_registry.NotRegistered:
            print 'policy.control: ERROR: task {0} was not found'.format(name)
            raise
        assert isinstance(task, BaseTask), 'type(task): {0}'.format(type(task))
        return task.__class__


    @Panel.register
    def update_tasks_settings(panel, tasks_settings):
        # task_settings = dict: { taskname: { attrname: value, ... }, ... }
        panel.logger.debug('policy.control: update_tasks_settings()')
        for taskname, settings in tasks_settings.iteritems():
            # TODO: wrap this in try..except so one failure doesn't stop setting all settings.
            taskcls = _get_task_class(taskname)
            for attr,val in settings.iteritems():
                setattr(taskcls, attr, val)
        return {"ok": "task settings updated reset"}
        

    @Panel.register
    def get_task_settings(panel, tasknames=None, setting_names=None):
        panel.logger.debug('policy.control: get_task_settings()')
        if tasknames is None:
            tasknames = tasks_registry.data
        allsettings = {}
        for taskname in tasknames:
            taskcls = _get_task_class(taskname)    
            data = dict((attr, taskcls.__dict__[attr]) for attr in setting_names 
                                                       if attr in taskcls.__dict__)
            allsettings[taskname] = data
        return allsettings
        
        
    @Panel.register
    def get_all_task_settings(panel, setting_names):
        panel.logger.debug('policy.control: get_all_task_settings()')
        allsettings = {}
        for taskname in tasks_registry.data:
            taskcls = _get_task_class(taskname)    
            data = dict((attr, taskcls.__dict__[attr]) for attr in setting_names 
                                                       if attr in taskcls.__dict__)
            allsettings[taskname] = data
        return allsettings


    @Panel.register
    def restore_task_settings(panel, restore_data):
        # restore_data = dict: { taskname: (restore_dict, erase_list), ... }
        panel.logger.debug('policy.control: restore_task_settings()')
        for taskname, (restore, erase) in restore_data.iteritems():
            # TODO: catch taskname not found exceptions
            taskcls = _get_task_class(taskname)
            for attr,v in restore.iteritems():
                setattr(taskcls, attr, v)
            for attr in erase:
                try:
                    delattr(taskcls, attr)
                except AttributeError:
                    pass

    #==============================================================================#
    @Panel.register
    def get_task_attribute(panel, taskname, attrname):
        panel.logger.debug('policy.control: get_task_attribute()')
        try:
            task = _get_task_class(taskname)
        except KeyError:
            panel.logger.error("Attempted to get %s for unknown task %s" % (
                attrname, taskname), exc_info=sys.exc_info())
            return {"error": "unknown task"}
        
        if not hasattr(task, attrname):
            msg = "Attempted to get an unknown attribute %s for task %s" % (
                   attrname, taskname)
            panel.logger.error(msg)
            return {"error": "unknown attribute"}
            
        return getattr(task, attrname)


    @Panel.register
    def set_task_attribute(panel, tasknames, attrname, value):
        panel.logger.debug('policy.control: set_task_attribute()')
        if isinstance(tasknames, basestring):
            tasknames = [tasknames]
        for taskname in tasknames:
            try:
                task = _get_task_class(taskname)
            except KeyError:
                panel.logger.error("Attempted to set %s for unknown task %s" % (
                    attrname, taskname), exc_info=sys.exc_info())
                return {"error": "unknown task"}
            
            if not hasattr(task, attrname):
                msg = "Attempted to set an unknown attribute %s for task %s" % (
                       attrname, taskname)
                panel.logger.error(msg)
                return {"error": "unknown attribute"}
            
            setattr(task, attrname, value)
        return {"ok": "new %s set successfully" % attrname}

    #==============================================================================#
    @Panel.register
    def prefetch_increment(panel, n):
        panel.consumer.qos.increment(n)
        return {'ok': 'incremented prefetch by {0}'.format(n) }

    @Panel.register
    def prefetch_decrement(panel, n):
        panel.consumer.qos.decrement(n)
        return {'ok': 'decremented prefetch by {0}'.format(n) }

    #==============================================================================#

