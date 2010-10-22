import datetime

from celery.decorators import task, periodic_task

#==============================================================================#
# These tasks are only for testing purposes.
@task
def print_time():
    print 'The time is now: {0}'.format(datetime.datetime.now())

@task()
def sum_numbers(a,b):
    print '{0} + {1} = {2}'.format(a,b,a+b)

@periodic_task(run_every=datetime.timedelta(minutes=2))
def periodic_hi():
    print 'I am saying "Hi".  You are reading me say "Hi".'
    
@task()
def silly_loop():
    i = 0
    while i<100000:
        i+=1
    
#@periodic_task(run_every=datetime.timedelta(minutes=2))    
#def silly_periodic_loop():
#    i = 0
#    while i<100000:
#        i+=1




