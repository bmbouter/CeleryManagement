import subprocess
import time
import collections
import sys
import signal
import traceback
from optparse import OptionParser

TERMINATE_ATTEMPTS_COUNT = 10
    
class ProcessSet(object):
    def __init__(self, procsargs, init_delay=1.0):
        print 'ProcessSet: Starting processes...'
        self.procs = []
        try:
            for i,args in enumerate(procsargs):
                print 'ProcessSet: Starting process #{0}...  '.format(i+1),
                if isinstance(args, collections.Sequence):
                    proc = subprocess.Popen(args, close_fds=True)
                elif isinstance(args, collections.Mapping):
                    args['close_fds'] = True
                    proc = subprocess.Popen(**args)
                else:
                    print
                    msg = 'ProcessSet: Bad process arguments!\n'
                    msg += '  process_arguments in runall_config.py must contain lists and/or dicts.'
                    msg += '  process_arguments[{0}] is: {1}.'.format(i,type(args))
                    raise RuntimeError(msg)
                self.procs.append(proc)
                time.sleep(init_delay)
                print 'pid: {0}'.format(proc.pid)
        except:
            self.terminate()
            raise
        
        if not self.all_running():
            self.terminate()
            raise RuntimeError("A process failed during initialization.")
        print 'ProcessSet: Processes started successfully...'
                    
    def __len__(self):
        return len(self.procs)
        
    def all_stopped(self):
        """Return True if all processes poll() methods return true.  In other 
           words, if they are all stopped.
        """
        return all((p.poll() is not None) for p in self.procs)
        
    def all_running(self):
        return all((p.poll() is None) for p in self.procs)
        
    def good(self):
        # every process is running or exited normally
        return all((p.returncode is None or p.returncode==0) for p in self.procs)
        
    def print_caught_exception(self):
        try:
            print 'ProcessSet: Caught exception:'
            traceback.print_exc()
        except:
            pass
        
    def terminate(self):
        print 'ProcessSet: Terminating processes...'
        for proc in self.procs:
            if proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait()
                except OSError:
                    # Ignore "No such process"
                    pass
                
    def kill(self):
        if not self.all_stopped():
            print 'ProcessSet: Killing processes...'
            for proc in self.procs:
                if proc.poll() is None:
                    try:
                        proc.kill()
                    except OSError:
                        # Ignore "No such process"
                        pass
                
    def loop(self, interval=1.0):
        print 'ProcessSet: Entering loop...  (use CONTROL-C to quit)'
        try:
            while self.good():
                time.sleep(interval)
                
        except:
            self.print_caught_exception()
            print 'ProcessSet: Leaving loop on exception...'
            self.terminate()
            raise
            
        print 'ProcessSet: Leaving loop normally...'
        self.terminate()
        
    def cleanup(self, waittime=2.0):
        print 'ProcessSet: Cleaning up...'
        i = 0
        while i<TERMINATE_ATTEMPTS_COUNT and not self.all_stopped():
            self.terminate()
            time.sleep(0.5)
            i+=1
        print 'ProcessSet: Allowing extra time for processes to stop before killing them...'
        time.sleep(waittime)
        self.kill()

def parse_options():
    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config",
                      help="Configuration module", metavar="CONFIG",
                      default="runall_config")
    return parser.parse_args()
           
def main():
    opts,args = parse_options()
    configname = opts.config
    p = configname.rfind('.')
    config = __import__(configname, globals(), locals(), [], -1)
    if p != -1:
        config = config.getattr(config, configname[p+1:])
    
    ps = ProcessSet(config.process_arguments)
    try:
        ps.loop()
    except:
        pass
    ps.cleanup()
    print 'ProcessSet: Completed!'


main()
