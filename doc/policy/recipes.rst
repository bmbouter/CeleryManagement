
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
            # Runs every day at 3:00 AM.
            crontab(minute=0, hour=3)
        
        condition:
            # Checks that no tasks of type "tasks.my_task" succeeded between 
            # 2:00 and 3:00 AM today.  If this is true, then the apply section 
            # is executed.
            0 == stats.tasks_succeeded( interval=(today(timestr='2:00'),
                                                  today(timestr='3:00')),
                                        tasknames='tasks.my_task' )
        
        apply:
            # Assemble components of the email.
            subject =       'Celery Info: tasks.my_task did not succeed.'
            msg =          ('The tasks.my_task Task did not succeed between '
                            '2am and 3am this morning.')
            from_email =    'celery_notice@example.com'
            recipient_list = ['admin@example.com']
            
            # Send the email.
            send_email(subject, msg, from_email, recipient_list)



Add/Remove Worker Subprocesses Depending on Average Wait Time
=============================================================

.. code-block:: policy
    
    # Policy to handle an excessively low wait time.
    policy:
        schedule:
            # Run every 10 minutes, on Monday through Friday.
            crontab(minute='*/10', day_of_week='mon,tue,wed,thu,fri')
            
        condition:
            # A condition combines multiple lines using AND.  Therefore, both 
            # of the following expressions must evaluate to True.
            
            # Check that there has been at least one task of type 
            # "tasks.my_task" to have succeeded on worker "worker1" over the 
            # past hour.
            0 != stats.tasks_succeeded( interval=datetime.timedelta(hours=1), 
                                        tasknames='tasks.my_task', 
                                        workers='worker1' )
            # Check if the mean wait time of those same tasks has dipped below 
            # 15 seconds.
            15.0 > stats.mean_waittime( interval=datetime.timedelta(hours=1), 
                                        tasknames='tasks.my_task', 
                                        workers='worker1' )
            
        apply:
            # Decrease the number of subprocesses that worker "worker1" is 
            # running.
            workers['worker1'].subprocesses.decrement()
        

.. code-block:: policy

    # Policy to handle an excessively high wait time.
    policy:
        schedule:
            # Run every 10 minutes, on Monday through Friday.
            crontab(minute='*/10', day_of_week='mon,tue,wed,thu,fri')
            
        condition:
            # Check that there has been at least one task of type 
            # "tasks.my_task" to have succeeded on worker "worker1" over the 
            # past hour.
            0 != stats.tasks_succeeded( interval=datetime.timedelta(hours=1), 
                                        tasknames='tasks.my_task', 
                                        workers='worker1' )
            # Check if the mean wait time of those same tasks has risen above 
            # 60 seconds.
            60.0 < stats.mean_waittime( interval=datetime.timedelta(hours=1), 
                                        tasknames='tasks.my_task', 
                                        workers='worker1' )
            
        apply:
            # Increase the number of subprocesses that worker "worker1" is 
            # running.
            workers['worker1'].subprocesses.increment()









