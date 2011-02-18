
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

The standard modules :mod:`datetime`, :mod:`time`, :mod:`calendar` and :mod:`math` are 
available in all policy sections.  Also available are two utility functions: 
``now()`` and ``today()``.  The former returns the current time as a 
``datetime.datetime`` object.  The latter returns the current date as a 
``datetime.date`` object.

Many of the standard builtin functions are available.  But some, like 
:func:`eval()` and :func:`__import__()` are not allowed.  The following are available::

    abs all any basestring bin bool bytearray callable chr cmp complex dict 
    divmod enumerate filter float format frozenset hash help hex id int 
    isinstance issubclass iter len list long map max memoryview min next 
    oct ord pow print range reduce repr reversed round set slice sorted str 
    sum tuple unichr unicode xrange zip
        
    
The following standard builtin constants are also available::

    True, False, None
    
The following Celery states are available as constants::
    
    PENDING, RECEIVED, STARTED, SUCCESS, FAILURE, REVOKED, RETRY
    
The following names provide access to the APIs described below:

    :data:`tasks`, :data:`workers`, :data:`stats`
    

.. _collection: collections_

Collections
===========

The APIs for :data:`tasks` and :data:`workers` follow the same general pattern.  This is 
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

The following description of the "Collection" class is for documentation 
purposes only.  It may be implemented in using any means which provides 
equivalent behavior.  Indeed, there may not even be a class by this name.
    
.. class:: Collection

    A class which provides access to an item or items within a homogeneous 
    group of objects.  Currently, two Collections are available: ``tasks`` and 
    ``workers``.  The user may not create objects of this class.

    .. method:: __getitem__(itemname)
   
        :param itemname: A single itemname as a string.
        :returns: An object which allows the item's attributes to be queried.
      
    .. method:: __setitem__(itemnames, value)
   
        :param itemnames: A single itemname as a string, or an iterable of itemnames.
        :returns: An object which allows setting of the items' attributes.
      
    .. method:: all()
   
        :returns: An object which allows setting the attributes of *all* items within the collection.


Tasks Collection
~~~~~~~~~~~~~~~~

.. data:: tasks

    An instance of :class:`Collection` that allows one to inspect and modify 
    selected Celery Task class attributes.  The methods on this object return 
    instances of :class:`TaskItem`.

.. class:: TaskItem
    
    An object which represents one or more Celery Task types.  Such an object 
    may be retrieved via the :data:`tasks` object within a Policy.
    
    .. attribute:: ignore_result
        
        bool
    
    .. attribute:: routing_key
        
        str or None
    
    .. attribute:: exchange
        
        str or None
    
    .. attribute:: default_retry_delay
        
        int
        
    .. attribute:: rate_limit
        
        str or None
    
    .. attribute:: store_errors_even_if_ignored
        
        bool
    
    .. attribute:: acks_late
        
        bool
    
    .. attribute:: expires
        
        int or None




Workers Collection
~~~~~~~~~~~~~~~~~~

.. data:: workers

    An instance of :class:`Collection` that allows one to inspect and modify 
    selected attributes of running Celery Workers.  The methods on this object 
    return instances of :class:`WorkerItem`.

.. class:: WorkerItem
    
    An object which represents one or more running Celery Workers.  Such an 
    object may be retrieved via the :data:`workers` object within a Policy.
    
    .. attribute:: prefetch
    
        The object returned has the following methods:
        
        .. method:: increment([n])
                    decrement([n])
        
            If not given, the `n` argument defaults to 1.
            
        .. method:: get()
        
            TODO
    
    .. attribute:: subprocesses
    
        The object returned has the following methods:
        
        .. method:: increment([n])
                    decrement([n])
        
            If not given, the `n` argument defaults to 1.
            
        .. method:: get()
        
            TODO


Status & History
================

.. data:: stats
    
    The `stats` object provides several methods to inspect the current status 
    and past performance of tasks.  The following are the available methods:
    
    .. method:: tasks(states=None, interval=None, workers=None, tasknames=None)
    
        The number of tasks that meet the given conditions.
        
        :param states: A single Celery state constant or an iterable of such 
            constants.
            
        :param interval: A single datetime.timedelta object, or a pair of 
            datetime.timedelta and/or datetime.datetime objects (as a tuple).  
            When it is a single timedelta object, the interval spans the time 
            from timedelta seconds [1]_ before now up to now.  When it is a 
            pair, the interpretation depends on the element types:
            
            ``(timedelta i, datetime j)``:
                The time between time `j` and `i` seconds [1]_ before time `j`.
            ``(datetime i, timedelta j)``:
                The time between time `i` and `j` seconds [1]_ after time `i`.
            ``(timedelta i, timedelta j)``:
                The time between `i` seconds [1]_ before now and `j` seconds [1]_ 
                before now.
            ``(datetime i, datetime j)``:
                The time between time `i` and time `j`.
                
            In all cases, the calculated date pairs are adjusted so the left 
            datetime is less than the right.
            
        :param workers: TODO
        
        :param tasknames: TODO
        

    .. method:: tasks_failed(interval=None, workers=None, tasknames=None)
    
        The number of tasks that meet the given conditions and that have 
        failed.  The parameters `interval`, `workers`, and `tasknames` have the 
        same meaning as in :meth:`tasks`.
    
    .. method:: tasks_succeeded(interval=None, workers=None, tasknames=None)
    
        The number of tasks that meet the given conditions and that have 
        succeeded.  The parameters `interval`, `workers`, and `tasknames` have 
        the same meaning as in :meth:`tasks`.
        
    .. method:: tasks_revoked(interval=None, workers=None, tasknames=None)
    
        The number of tasks that meet the given conditions and that have been 
        revoked.  The parameters `interval`, `workers`, and `tasknames` have 
        the same meaning as in :meth:`tasks`.
        
    .. method:: tasks_ready(interval=None, workers=None, tasknames=None)
    
        The number of tasks that meet the given conditions and that are in a 
        ready state.  The parameters `interval`, `workers`, and `tasknames` 
        have the same meaning as in :meth:`tasks`.
        
    .. method:: tasks_sent(interval=None, workers=None, tasknames=None)
    
        The number of tasks that meet the given conditions and that are in an 
        unready state.  The parameters `interval`, `workers`, and `tasknames` 
        have the same meaning as in :meth:`tasks`.

    .. method:: mean_waittime(states, interval, workers, tasknames)
    
        The average wait time of the tasks that meet the given conditions.
        
    .. method:: mean_runtime(states, interval, workers, tasknames)
    
        The average run time of the tasks that meet the given conditions.
        
.. [1] ``timedelta`` is not restricted to seconds, but using some concrete unit 
   of time here is clearer.  

Schedules
=========

The schedule section provides functions that (strangely enough) can create 
schedules.  The evaluation of the section must result in a schedule object.

.. function:: crontab(minute, hour, day_of_week)
    
    This function creates a schedule that allows cron-like scheduling.  The 
    class itself is provided by Celery, so please see the `documentation 
    there`__ for more infomation.
    
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

::

    x = stats.tasks()
    
The number of tasks sent.  (This will not be all tasks ever sent because 
old records in the database are cleared periodically.)
    
::

    x = stats.tasks(interval=datetime.timedelta(hour=1))
    
The number of tasks sent over the last hour.
    
::
    
    x = stats.tasks(interval=(datetime.timedelta(hour=2),datetime.timedelta(hour=1)))
    
The number of tasks sent between one hour and two hours ago.

::

    x = stats.tasks(tasknames="my_task")
    
The number of tasks of type ``my_task`` sent.

::

    x = stats.tasks(tasknames=["my_task","your_task"])
    
The number of tasks of type ``my_task`` `or` ``your_task`` sent.

::

    x = tasks["my_task"].ignore_result
    
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



