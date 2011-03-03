
.. _policies-api:

Policies API
############

Policies consist of three sections: schedule, condition, and apply.  The API 
varies depending on the section it is in.  The first section, `schedule`, 
provides the most restrictive API since its only purpose is to return a 
schedule object.  The `condition` section is also somewhat restricted, and the 
`apply` section has the most feature-filled API.

See :ref:`Policies Overview <policies-overview>` for information about how 
policies may be used.

.. contents::


Task and Worker Settings
========================

This sections discusses how to check :ref:`tasks' <tasks-collection>` and 
:ref:`workers' <workers-collection>` settings as well as how to modify those 
settings.  A similar API, called a collection, is followed for both.  

.. _collection: collections_

Collections
~~~~~~~~~~~

The pattern that is followed for accessing both tasks and workers settings is 
called a collection.  Using this interface, one may access one, many, or all 
tasks or workers.

In the policy API, the collections are referred to by the names ``tasks`` for 
tasks, and ``workers`` for workers.  Please see their specific topics below for 
the details of accessing tasks and workers.

Here is the general pattern for accessing specific collection members::

    collection.all()                    # access all collection members
    collection['NAME']                  # access a specific collection member
    collection[('NAME1','NAME2',...)]   # access multiple collection members
    
The first example above accesses all members of the collection.  The object 
returned can be used to set the same setting on all of those members.  The 
second example accesses only the single named object.  The returned value can 
be used to get or set the settings on that specific object.  The third example 
accesses multiple specificly-named objects.  The returned value can be used to 
set the same setting on those specifically-named objects.

.. note:: The Collections API is designed to be simple and intuitive.  
   One manifestiation of this is that they always return single values.  
   Because the same setting may have different values on different objects, it 
   makes no sense to get a single setting from multiple objects.  As a result, 
   settings may be retrieved for only one named object at a time. 
   
   For example::
   
        val = tasks.all().ignore_result             # This will raise an exception.
        val = tasks['tasks.MyTask'].ignore_result   # This is OK.
        
.. _tasks-collection:

Tasks Collection
~~~~~~~~~~~~~~~~

.. data:: tasks

    The tasks collection available to policies.  This allows one to inspect and 
    modify selected Celery :ref:`Task <guide-tasks>` attributes.  The methods 
    on this object return instances of :class:`TaskItem`.

.. class:: TaskItem
    
    An object which represents one or more Celery Task types.  Such an object 
    may be retrieved via the :data:`tasks` object within a Policy.
    
    To retrieve the routing_key on a Task named tasks.MyTask::
        
        x = tasks['tasks.MyTask'].routing_key
        
    To set the ignore_result attribute on the same Task::
        
        tasks['tasks.MyTask'].ignore_result = True
        
    The following Task attributes are available:
    
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

        
.. _workers-collection:

Workers Collection
~~~~~~~~~~~~~~~~~~

.. data:: workers

    The workers collection available to policies.  This allows one to inspect 
    and modify selected attributes of running Celery 
    :ref:`Workers <guide-worker>`.  The methods on this object return instances 
    of :class:`WorkerItem`.

.. class:: WorkerItem
    
    An object which represents one or more running Celery Workers.  Such an 
    object may be retrieved via the :data:`workers` object within a Policy.
    
    To get the prefetch value for a Worker named myworker.example.org::
        
        x = workers["myworker.example.org"].prefetch.get()
        
    To increment the number of subprocesses on the same worker::
        
        workers["myworker.example.org"].subprocesses.increment()
    
    .. attribute:: prefetch
    
        The object returned has the following methods:
        
        .. method:: increment([n])
                    decrement([n])
        
            If not given, the `n` argument defaults to 1.
            
        .. method:: get()
        
            Return the worker's current prefetch value.
    
    .. attribute:: subprocesses
    
        The object returned has the following methods:
        
        .. method:: increment([n])
                    decrement([n])
        
            If not given, the `n` argument defaults to 1.
            
        .. method:: get()
        
            Return the number of subprocesses the worker has.

Task and Worker Stats
=====================

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


.. _policy-schedule:

Policy Schedule
===============

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


Common API
==========

Although using a subset of Python, policies still provide many of the 
language's built-in functions, constants and a few selected modules.
    
Utilities
~~~~~~~~~

.. function:: now()
    
    Returns the current time as a :class:`datetime.datetime` object.  (The 
    datetime module is also available to policies.)
    
.. function:: today([offset_days, timestr, time])
    
    Returns the current date as a :class:`datetime.datetime` object.  (The 
    datetime module is also available to policies.)  All arguments are 
    optional, and only keyword arguments are allowed.
    
    If no arguments are provided, the time defaults to ``00:00:00`` (midnight).  
    However, some keyword arguments are offered which can change this behavior.
        
    :keyword int offset_days: An integer which can set the date forward or 
                              backward from the current date.
                          
    :keyword str timestr: A string representing a time which will be used in 
                          the returned datetime object.  The string's format is 
                          as follows: ``HH:MM:SS.mmmmmm``
                      
                          - ``HH``, ``MM``, ``SS`` are the minutes, hours, and 
                            seconds.
                          - ``mmmmmm`` is the microseconds, which can be 0-6 
                            digits.
                          
                          The seconds and microseconds are optional.
                      
    :keyword tuple time: A tuple representing a time which will be used in the 
                         returned datetime object.  The elements much be 
                         integers which represent: hours, minutes, seconds, and 
                         microseconds.  The seconds and microseconds are 
                         optional.
                   
    If both *timestr* and *time* are provided, only *timestr* will be used.

Email
-----

.. function:: send_email(subject, message, from_email, recipient_list, [auth_user [, auth_password]])

    Sometimes, a policy does not need to (or is not able to) respond 
    automatically to the condition it finds.  This function allows a policy to 
    send you an email in such situations.  It is built on top of Django_'s 
    email feature.
    
    :param str subject: The subject of the email message, as a string.
    :param str message: The content of the email message, as a string.
    :param str from_email: The email address that will appear in the *from* field.
    :param list recipient_list: A list of email addresses to which to send the email.
    :param str auth_user: Username for the SMTP server.  If not given, 
                          Django will use the ``EMAIL_HOST_USER`` setting.
    :param str auth_password: Password for the SMTP server.  If not given, 
                              Django will use the ``EMAIL_HOST_PASSWORD`` 
                              setting.

Celery States
-------------
    
The following :ref:`Celery states <task-states>` are available as 
constants::
    
    PENDING, RECEIVED, STARTED, SUCCESS, FAILURE, REVOKED, RETRY

Available Standard Modules
~~~~~~~~~~~~~~~~~~~~~~~~~~

- :mod:`datetime`
- :mod:`time`
- :mod:`calendar`
- :mod:`math`

Python Builtins
~~~~~~~~~~~~~~~

Many of the standard builtin functions are available.  But some, like 
:func:`eval()` and :func:`__import__()` are not allowed. The following builtin 
functions are available:

==================  ==================  ===================  ==================  ==================
..                  ..                  Built-in Functions   ..                  ..
==================  ==================  ===================  ==================  ==================
:func:`abs`         :class:`dict`       :func:`int`          :func:`next`        :func:`slice`       
:func:`all`         :func:`divmod`      :func:`isinstance`   :func:`oct`         :func:`sorted`      
:func:`any`         :func:`enumerate`   :func:`issubclass`   :func:`ord`         :func:`str`         
:func:`basestring`  :func:`filter`      :func:`iter`         :func:`pow`         :func:`sum`         
:func:`bin`         :func:`float`       :func:`len`          :func:`print`       :func:`tuple`       
:func:`bool`        :func:`format`      :func:`list`         :func:`range`       :func:`unichr`      
:func:`bytearray`   :class:`frozenset`  :func:`long`         :func:`reduce`      :func:`unicode`     
:func:`callable`    :func:`hash`        :func:`map`          :func:`repr`        :func:`xrange`      
:func:`chr`         :func:`help`        :func:`max`          :func:`reversed`    :func:`zip`
:func:`cmp`         :func:`hex`         :class:`memoryview`  :func:`round`       
:func:`complex`     :func:`id`          :func:`min`          :class:`set`        
==================  ==================  ===================  ==================  ==================

The following builtin functions are *not* available (this list may be 
incomplete):

======================  ======================  ===================
..                      Prohibited Functions    ..
======================  ======================  ===================
:func:`compile`         :func:`globals`         :func:`raw_input`     
:func:`eval`            :func:`hasattr`         :func:`reload`        
:func:`execfile`        :func:`input`           :func:`setattr`       
:func:`file`            :func:`locals`          :func:`type`          
:func:`getattr`         :func:`open`            :func:`__import__`   
======================  ======================  =================== 

The following standard builtin constants are also available::

    True, False, None
    
Examples
========

The following examples show how to use various portions of the policies API.  
See :ref:`Policy Recipes <policy-recipes>` for examples of entire policies.

::

    x = stats.tasks()   # 1

1. The number of tasks sent.  (This will not be all tasks ever sent because 
   old records in the database are cleared periodically.)

    
::

    x = stats.tasks(interval=datetime.timedelta(hour=1))    # 2
    
2. The number of tasks sent over the last hour.
    
::
    
    x = stats.tasks(interval=(datetime.timedelta(hour=2),datetime.timedelta(hour=1)))    # 3
    
3. The number of tasks sent between one hour and two hours ago.

::

    x = stats.tasks(tasknames="my_task")    # 4
    
4. The number of tasks of type ``my_task`` sent.

::

    x = stats.tasks(tasknames=["my_task","your_task"])      # 5
    
5. The number of tasks of type ``my_task`` `or` ``your_task`` sent.

::

    x = tasks["my_task"].ignore_result      # 6
    
6. Get the ``ignore_result`` setting for tasks of type ``my_task``.


Availability by Policy Section
==============================

==========  ==========  ==========  ======
..          schedule    condition   apply
==========  ==========  ==========  ======
Common API      ✓           ✓        ✓     
send_email                            ✓    
crontab         ✓                          
stats                        ✓        ✓     
tasks                                 ✓    
workers                               ✓
==========  ==========  ==========  ======


.. _Django: http://www.djangoproject.com/


