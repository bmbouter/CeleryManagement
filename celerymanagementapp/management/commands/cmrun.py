import sys
import os
import signal

from multiprocessing import Process, Queue, current_process
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from celery.bin import celeryev


class CmEvCommand(celeryev.EvCommand):
    def run_evcam(self, *args, **kwargs):
        from celerymanagementapp.snapshot.snapshot import evcam
        self.set_process_status("cam")
        kwargs["app"] = self.app
        return evcam(*args, **kwargs)
        
def run_policy_manager(**options):
    from celerymanagementapp.policy import main
    from djcelery.app import app
    main.policy_main(app=app, **options)
    

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-F', '--frequency', '--freq',
                   action="store", dest="frequency",
                   type="float", default=1.0,
                   help="Recording: Snapshot frequency."),
        make_option('-r', '--maxrate',
                   action="store", dest="maxrate", default=None,
                   help="Recording: Shutter rate limit (e.g. 10/m)"),
        make_option('-l', '--loglevel',
                    action="store", dest="loglevel", default="WARNING",
                    help="Loglevel. Default is WARNING."),
        make_option('-f', '--logfile',
                   action="store", dest="logfile", default=None,
                   help="Log file. Default is <stderr>"),
        )
    
    args = ''
    help = '''The CeleryManagement event handler that records Celery events in 
the database.'''
    
    def handle(self, *args, **options):
        options['camera'] = 'celerymanagementapp.snapshot.snapshot.Camera'
        options['dump'] = False
        options['prog_name'] = 'cmrun'
            
        main(*args, **options)
        
        
        
def get_policy_options(options):
    newopts = {}
    if 'loglevel' in options:
        newopts['loglevel'] = options['loglevel']
    return newopts
    
def get_ev_options(options):
    return options.copy()
        
        
def main(*args, **options):
    from djcelery.app import app
    ev = CmEvCommand(app=app)
    
    policy_options = get_policy_options(options)
    ev_options = get_ev_options(options)
    
    # The name is set in the following because it shows up in log messages.
    p = Process(target=run_policy_manager, args=(), kwargs=policy_options, name='policy-manager')
    p.start()
    try:
        ev.run(*args, **ev_options)
    finally:
        # try to join, if it doesn't, then force it to terminate
        if p.is_alive():
            pid = p.pid
            os.kill(pid, signal.SIGINT)
            p.join(5.0)
            if p.is_alive():
                print 'The policy_manager process did not stop on its own.  '\
                      'Trying to terminate it...'
                p.terminate()
        p.join()






