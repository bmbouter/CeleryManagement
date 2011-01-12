from celery.task.control import broadcast, inspect

from celerymanagementapp.policy.manager import get_task_settings

def condense_broadcast_result(result):
    checkval = None
    first_iteration = True
    for k,v in result.iteritems():
        if first_iteration:
            checkval = v
            first_iteration = False
        assert v==checkval, 'v!=checkval:\nv: {0}\ncheckval: {1}\n'.format(v,checkval)
    return checkval


def assert_task_settings(taskname, expected_settings):
    expected_settings = expected_settings.copy()
    settings_by_worker = get_task_settings(workername=None,tasknames=[taskname])
    settings = condense_broadcast_result(settings_by_worker)
    assert taskname in settings
    settings = settings[taskname]
    m = 'task {0} settings do not match\nactual: {1}\nexpected: {2}\n'
    assert settings==expected_settings, m.format(settings, expected_settings)
    
    ## settings: { taskname1: { attr1: val1, ...}, ...} 
    #for taskname, tasksettings in settings:
    #    assert taskname in expected_settings, 'task {0} not expected'.format(taskname)
    #    expected_tasksettings = expected_settings.pop(taskname)
    #    m = 'task {0} settings do not match\nactual: {1}\nexpected: {2}\n'
    #    assert tasksettings==expected_tasksettings, m.format(tasksettings, expected_tasksettings)
    #assert len(expected_settings)==0, 'these settings not found:\n{0}'.format(expected_settings)


def print_task_settings(tasknames):
    import pprint
    settings_by_worker = get_task_settings(workername=None, tasknames=tasknames)
    settings = condense_broadcast_result(settings_by_worker)
    print 'task settings:'
    s = pprint.pformat(settings)
    print s
    print ''
    
def set_task_setting(taskname, attrname, value):
    r = broadcast('set_task_attribute', arguments={'tasknames': taskname, 
                  'attrname': attrname, 'value': value,}, reply=True)
    return
    
def test():
    # cmrun must be running, at least one celeryd instance must be running
    print 'running test...'
    simple_test = 'celerymanagementapp.testutil.tasks.simple_test'
    assert_task_settings(simple_test, {'ignore_result': True})
    set_task_setting(simple_test, 'store_errors_even_if_ignored', True)
    assert_task_settings(simple_test, {'ignore_result': True, 
                                       'store_errors_even_if_ignored': True})
    print_task_settings([simple_test])


