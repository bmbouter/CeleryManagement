from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse as urlreverse

from celerymanagementapp.testutil.load_generator import generate_load
from celerymanagementapp.testutil import tasks as tasksmod

class Command(BaseCommand):
    """
        A django command for launching some Celery tasks.  The results can be 
        viewed using CeleryManagement.  Both celeryd and celeryev must be 
        launched with appropriate arguments in order for the tasks to be 
        recorded -- for instance, they must all be using the same settings 
        module.
        
        Usage:
            django-admin.py taskdemo [task task ...] [options]
            
        task:
            A task in the celerymanagementapp.taskutil.tasks module.  If none 
            are given, the default is "simple_test".
            
        options:
            --runtime N
                The time (in seconds) over which to execute the tasks.
                Default: 20.
            --burstsize N
                The burst size--the number of tasks to execute "at once".
                Default: 50.
            --expectedrate R
                The desired task throughput.  Bursts of tasks will be executed 
                as needed to meet this value.  This is a floating point number.
                Default: 10.0.
    """
    option_list = BaseCommand.option_list + (
        make_option('--runtime',
            action='store',
            type='int',
            dest='runtime',
            default=20,
            help='The time (in seconds) over which to execute the tasks.'),
        make_option('--burstsize',
            action='store',
            type='int',
            dest='burstsize',
            default=50,
            help='The burst size--the number of tasks to execute "at once".'),
        make_option('--expectedrate',
            action='store',
            type='float',
            dest='expectedrate',
            default=10.0,
            help='The desired task throughput.  Bursts of tasks will be executed as needed to meet this value.'),
        )
    
    args = '<task task ...>'
    help = 'Launches several tasks, the results of which can be viewed using CeleryManagement'
    
    #available_tasks = ['simple_test','print_time','silly_loop']
    
    def _get_available_task_names(self):
        import celery.task
        task_names = []
        names = [s for s in tasksmod.__dict__]
        for s in names:
            if isinstance(tasksmod.__dict__[s], celery.task.Task):
                task_names.append(s)
        return task_names
    
    def handle(self, *args, **options):
        tasks = []
        qtaskname = []
        
        # Get name of task(s) to execute.
        if len(args)==0:
            args = ['simple_test']
        available_tasks = self._get_available_task_names()
        for taskname in args:
            # TODO: allow importing of arbitrary tasks if the name contains a period.
            if taskname not in available_tasks:
                msg = '"{name}" is not a legal task.\n'
                msg += 'Please enter a fully-qualified task name, '
                msg += 'or one of the following built-in test tasks:\n  {tasks}'
                msg = msg.format(name=taskname, tasks=', '.join(available_tasks))
                raise CommandError(msg)
            tasks.append(getattr(tasksmod,taskname))
            qtaskname.append(tasksmod.__name__+'.'+taskname)
        
        # Determine urls of views.
        funcname1 = 'celerymanagementapp.views.visualize_throughput'
        urls = [ urlreverse(funcname1, kwargs={'taskname':taskname}) 
                 for taskname in qtaskname ]
        funcname2 = 'celerymanagementapp.views.visualize_runtimes'
        urls += [ urlreverse(funcname2, 
                  kwargs={'taskname':taskname, 'bin_count':20, 'bin_size':0.001, 
                          })##'runtime_min':0.0}) 
                  for taskname in qtaskname ]
        
        # Run the tasks
        print 'Launching tasks... (this may take a while)'
        count, secs = generate_load(tasks, options['expectedrate'],
                                    options['burstsize'], options['runtime'])
        print ''
        print 'Chosen tasks:\n    {0}'.format('\n    '.join(qtaskname))
        print 'Launched {0} tasks over {1:1.4} seconds.'.format(count, secs)
        print 'The average throughput was {0:1.4} tasks/sec.'.format(count/secs)
        print '\nTo view the results, please use the following urls: '
        print '    {0}'.format('\n    '.join(urls))
        print '(The last three items in the runtime visualization urls are for'
        print 'the minimum-runtime, bin-count and bin-size.  These parameters'
        print 'may be modified--the values shown are simply defaults.)\n'
        

