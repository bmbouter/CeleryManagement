
Policies API
############

Policies consist of three sections: schedule, condition, and apply.  The API 
varies depending on the section it is in.  The first section, `schedule`, 
provides the most restrictive API since its only purpose is to return a 
schedule object.  The `condition` section is also somewhat restricted, and the 
`apply` section has the most feature-filled API.


.. contents::


Common API
==========

The standard modules ``datetime``, ``time``, ``calendar`` and ``math`` are 
available in all policy sections.  Also available are two utility functions: 
``now()`` and ``today()``.  The former returns the current time as a 
``datetime.datetime`` object.  The latter returns the current date as a 
``datetime.date`` object.

Many of the standard builtin functions are available.  But some, like 
``eval()`` and ``__import__()`` are not allowed.  The following are available::

    abs all any basestring bin bool bytearray callable chr cmp complex dict 
    divmod enumerate filter float format frozenset hash help hex id int 
    isinstance issubclass iter len list long map max memoryview min next 
    oct ord pow print range reduce repr reversed round set slice sorted str 
    sum tuple unichr unicode xrange zip
        
    
The following standard builtin constants are also available::

    True, False, None
    
The following Celery states are available as constants::
    
    PENDING, RECEIVED, STARTED, SUCCESS, FAILURE, REVOKED, RETRY
    
The following names provide access to the APIs described below::

    tasks, workers, stats
    

.. _collection: collections_

Collections
===========

The APIs for tasks_ and workers_ follow the same general pattern.  This is 
probably easier to demonstrate with a couple of examples.::

    tasks.all().the_attribute = value
    tasks['taskname'].the_attribute = value
    tasks[('task1','task2','task3',)].the_attribute = value
    
The first example above assigns to the same attribute on all known task types.  
The second assigns to the attribute on only one task type.  The third example 
assigns to the same attribute on each of the explicitly listed task types.  

Retrieving values is more restricted.  The attribute can be retrieved from only 
one task type at a time.  Otherwise, a dict of attrbute values with task types 
as keys would be required.  This would be too complicated, especially for the 
common case where one is interested in only a single type.

Therefore, when retrieving values, only the following pattern is allowed::

    value = tasks['taskname'].the_attribute



Tasks
~~~~~

The `tasks` object is a collection_ that allows one to inspect and modify 
selected Task class attributes. The following attributes can be accessed 
through the `tasks` object::

    ignore_result                   (bool)
    routing_key                     (str, None)
    exchange                        (str, None)
    default_retry_delay             (int)
    rate_limit                      (str, None)
    store_errors_even_if_ignored    (bool)
    acks_late                       (bool)
    expires                         (int, None)




Workers
~~~~~~~

The `workers` object is a collection_ that allows one to inspect and modify 
selected worker attributes. The following attributes can be accessed through 
the `workers` object:

    ``prefetch``
        it has the following methods
            ``increment(n)``
            ``decrement(n)``
            
        If not given, the `n` argument defaults to 1.




Stats
=====

The stats object provides several methods to inspect the current status of 
tasks.  All arguments are optional and should be specified by keywords.
    
    ``tasks(states, interval, workers, tasknames)``
        The number of tasks that meet the given conditions.

    ``tasks_failed(interval, workers, tasknames)``
        The number of tasks that meet the given conditions and that have failed.
    
    ``tasks_succeeded(interval, workers, tasknames)``
        The number of tasks that meet the given conditions and that have 
        succeeded.
        
    ``tasks_revoked(interval, workers, tasknames)``
        The number of tasks that meet the given conditions and that have been 
        revoked.
        
    ``tasks_ready(interval, workers, tasknames)``
        The number of tasks that meet the given conditions and that are in a 
        ready state.
        
    ``tasks_sent(interval, workers, tasknames)``
        The number of tasks that meet the given conditions and that are in an 
        unready state.

    ``mean_waittime(states, interval, workers, tasknames)``
        The average wait time of the tasks that meet the given conditions.
        
    ``mean_runtime(states, interval, workers, tasknames)``
        The average run time of the tasks that meet the given conditions.
        

Schedules
=========

The schedule section provides functions that (strangely enough) can create 
schedules.  The evaluation of the section must result in a schedule object.

    crontab(minute, hour, day_of_week)
    
        This function creates a schedule that allows cron-like scheduling.  The 
        class itself is provided by Celery, so please see the `documentation 
        there`__ for more information.
        
        Examples (reproduced here from the Celery documentation):

        ``crontab()``
            Execute every minute.
            
        ``crontab(minute=0, hour=0)``
            Execute daily at midnight.
            
        ``crontab(minute=0, hour="*/3")``
            Execute every three hours: 3am, 6am, 9am, noon, 3pm, 6pm, 9pm.
            
        ``crontab(minute=0, hour=[0,3,6,9,12,15,18,21])``
            Same as previous.
            
        ``crontab(minute="*/15")``
            Execute every 15 minutes.
            
        ``crontab(day_of_week="sunday")``
            Execute every minute (!) at Sundays.
            
        ``crontab(minute="*", hour="*", day_of_week="sun")``
            Same as previous.
        
        ``crontab(minute="*/10", hour="3,17,22", day_of_week="thu,fri")``
            Execute every ten minutes, but only between 3-4 am, 5-6 pm and 
            10-11 pm on Thursdays or Fridays.
        
        ``crontab(minute=0, hour="*/2,*/3")``
            Execute every even hour, and every hour divisible by three. This 
            means: at every hour `except`: 1am, 5am, 7am, 11am, 1pm, 5pm, 7pm, 11pm
        
        ``crontab(minute=0, hour="*/5")``
            Execute hour divisible by 5. This means that it is triggered at 3pm, 
            not 5pm (since 3pm equals the 24-hour clock value of “15”, which is 
            divisible by 5).
        
        ``crontab(minute=0, hour="*/3,8-17")``
            Execute every hour divisible by 3, and every hour during office 
            hours (8am-5pm).

.. __: http://ask.github.com/celery/userguide/periodic-tasks.html#crontab-schedules


Examples
========

``x = stats.tasks()``
    The number of tasks sent.  (This will not be all tasks ever sent because 
    old records in the database are cleared periodically.)
    
``x = stats.tasks(interval=datetime.timedelta(hour=1))``
    The number of tasks sent over the last hour.
    
``x = stats.tasks(interval=(datetime.timedelta(hour=2),datetime.timedelta(hour=1)))``
    The number of tasks sent between one hour and two hours ago.

``x = stats.tasks(tasknames="my_task")``
    The number of tasks of type ``my_task`` sent.

``x = stats.tasks(tasknames=["my_task","your_task"])``
    The number of tasks of type ``my_task`` `or` ``your_task`` sent.

``x = tasks["my_task"].ignore_result``
    Get the ``ignore_result`` setting for tasks of type ``my_task``.

API by Section
==============

::

    schedule
        crontab
        
    condition
        stats
        
    apply
        stats
        tasks
        workers



