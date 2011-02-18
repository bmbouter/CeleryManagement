import signal
import subprocess
import time
import sys

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

WAIT_SLEEP_INTERVAL = 0.05


class Proc(object):
    
    def __init__(self, basecmd, name, args):
        args = ['python', basecmd, name] + args
        self.name = name
        self.error = False
        self.proc = None
        self._start(args)
        
    def _start(self, args):
        if self.error:
            raise RuntimeError('Attempted to start process after error.')
        try:
            self.proc = subprocess.Popen(args)
        except Exception:
            self.error = True
            raise
        
    def stop(self, waittime=None):
        proc = self.proc
        if proc is not None and proc.poll() is None:
            proc.send_signal(signal.SIGINT)  # ctrl-C
            if self._wait(waittime) is None: # if wait() times out...
                print "Timeout while trying to stop: {0}.".format(self.name)
                proc.terminate()
                proc.wait()
                
    def _wait(self, timeout=0):
        if timeout and timeout > 0:
            assert WAIT_SLEEP_INTERVAL > 0.
            timeout += time.time()
            while time.time() < timeout and not self.is_stopped():
                time.sleep(WAIT_SLEEP_INTERVAL)
            return self.proc.returncode
        else:
            return self.proc.wait()
        
    def is_stopped(self):
        return self.proc is None  or  self.proc.poll() is not None

    
class Processes(object):
    def __init__(self, basecmd=None):
        self.basecmd = basecmd or 'django-admin.py'
        self.procs = {}
        self.error = False
        
    def _start(self, procname, args):
        if procname in self.procs:
            raise RuntimeError('Attempted to restart failed process.')
        if self.error:
            raise RuntimeError('Attempted to start process after error.')
        
        try:
            print 'cmrun: starting {0}.'.format(procname)
            proc = Proc(self.basecmd, procname, args)
            self.procs[procname] = proc
        except Exception:
            print 'cmrun: Error! Exception while starting {0}.'.format(procname)
            self.stop()
            self.error = True
            raise
        
    def start_cmevents(self, args):
        self._start('cmevents', args)
        
    def start_cmpolicy(self, args):
        self._start('cmpolicy', args)
        
    def stop(self):
        for name, proc in self.procs.iteritems():
            print 'cmrun: stopping {0}.'.format(name)
            proc.stop(8.0)
        
    def is_stopped(self):
        return all(proc.is_stopped() for proc in self.procs.itervalues())

        
base_optslist = [opt.dest for opt in BaseCommand.option_list]
base_optslist += ['loglevel','logfile']

ev_optslist = base_optslist + [
    'frequency', 'maxrate',
    ]

po_optslist = base_optslist + []

def make_args(args, options, optslist):
    args = list(args)
    endargs = []
    for k,v in options.iteritems():
        if k in optslist and v is not None:
            if k in ['settings','pythonpath']:
                endargs.extend(['--'+k, '{0}'.format(v)])
            else:
                args.extend(['--'+k, '{0}'.format(v)])
    args += endargs
    return args
        
def run(args, options):
    evargs = make_args(args, options, ev_optslist)
    poargs = make_args(args, options, po_optslist)
    procs = Processes(sys.argv[0])
    try:
        procs.start_cmevents(evargs)
        procs.start_cmpolicy(poargs)
        while not procs.is_stopped():
            time.sleep(2.0)
    except KeyboardInterrupt, SystemExit:
        pass
    finally:
        procs.stop()


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
    help = '''The CeleryManagement main process.'''
    
    def handle(self, *args, **options):
        run(args, options)
        







