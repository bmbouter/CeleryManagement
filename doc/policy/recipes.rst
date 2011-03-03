
.. _policy-recipes:

Policy Recipes
##############

This section provides some example policies and explains how they work.


.. contents::


Email When Task is Not Completed
================================

.. code-block:: policy

    policy:
        schedule:
            crontab()
        condition:
            0 == stats.tasks_succeeded( interval=(today(timestr='2:00'),
                                                  today(timestr='3:00')),
                                        tasknames='tasks.my_task' )
        apply:
            msg = 'The tasks.my_task Task did not succeed between 2am and 3am this morning.'
            from_email  =  'celery_notice@example.com'
            recipient_list = ['admin@example.com']
            send_email('Celery Info: tasks.my_task did not succeed.', msg,
                       from_email, recipient_list)



Add/Remove Worker Subprocesses Depending on Average Wait Time
=============================================================

