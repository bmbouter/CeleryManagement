from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from celery.events import EventReceiver
from celery.app import app_or_default

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        # make_option('-l', '--loglevel',
                    # action="store", dest="loglevel", default="WARNING",
                    # help="Loglevel. Default is WARNING."),
        # make_option('-f', '--logfile',
                   # action="store", dest="logfile", default=None,
                   # help="Log file. Default is <stderr>"),
        )
    
    args = ''
    help = '''A debugging tool that prints all Celery events.'''
    
    def handle(self, *args, **options):
        main()


def main():
    
    def print_event(event):
        type = event.pop('type')
        s = 'Event: {0}\n'.format(type)
        keys = event.keys()
        keys.sort()
        for k in keys:
            v = event[k]
            s += '    {0}: {1}\n'.format(k,v)
        print s
    
    print 'Initializing event listener.'
    app = app_or_default(None)
    conn = app.broker_connection()
    recv = EventReceiver(conn, handlers={'*': print_event}, app=app)
    
    try:
        try:
            print 'Listening for events...  (use Ctrl-C to exit)'
            recv.capture(limit=None)
        except KeyboardInterrupt, SystemExit:
            raise SystemExit
        except Exception:
            import traceback
            print 'Exception while listening for events:\n'
            traceback.print_exc()
            
    finally:
        conn.close()
    


