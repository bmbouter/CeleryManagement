from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-l', '--loglevel',
                    action="store", dest="loglevel", default="WARNING",
                    help="Loglevel. Default is WARNING."),
        make_option('-f', '--logfile',
                   action="store", dest="logfile", default=None,
                   help="Log file. Default is <stderr>"),
        )
    
    args = ''
    help = '''The CeleryManagement Policy manager.'''
    
    def handle(self, *args, **options):
        from celerymanagementapp.policy import main
        from djcelery.app import app
        main.policy_main(app=app, **options)
        




