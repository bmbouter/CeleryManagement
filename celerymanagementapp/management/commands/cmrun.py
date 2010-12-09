import sys

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from djcelery.app import app
from celery.bin import celeryev


class CmEvCommand(celeryev.EvCommand):
    def run_evcam(self, *args, **kwargs):
        from celerymanagementapp.snapshot.snapshot import evcam
        self.set_process_status("cam")
        kwargs["app"] = self.app
        return evcam(*args, **kwargs)


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
                    action="store", dest="loglevel", default="INFO",
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
            
        ev = CmEvCommand(app=app)
        ev.run(*args, **options)


