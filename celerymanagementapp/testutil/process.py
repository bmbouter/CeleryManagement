import subprocess
import signal
import time

DEFAULT_CMDBASE = 'django-admin.py'
DEFAULT_PYPATH = '.'
DEFAULT_SETTINGS = None #'testcelery_settings'

WAIT_SLEEP_INTERVAL = 0.05


#==============================================================================#
class TimeoutError(Exception):
    pass


#==============================================================================#
class Process(object):
    timeout_close = 1.0
    timeout_terminate = 1.0
    
    def __init__(self, *args, **kwargs):
        self.proc = subprocess.Popen(*args, **kwargs)
        
    def poll(self):
        return self.proc.poll()
        
    def is_stopped(self):
        return self.proc.poll() is not None
        
    def wait(self, timeout=0):
        if timeout and timeout > 0:
            assert WAIT_SLEEP_INTERVAL > 0.
            timeout += time.time()
            while time.time() < timeout and not self.is_stopped():
                time.sleep(WAIT_SLEEP_INTERVAL)
            return self.proc.returncode
        else:
            return self.proc.wait()
        
    def close(self):
        self.proc.send_signal(signal.SIGINT)
        
    def close_and_wait(self, timeout):
        self.close()
        if self.wait(timeout) is None:
            raise TimeoutError()
        return self.proc.returncode
        
    def terminate(self):
        self.proc.terminate()
        
    def kill(self):
        self.proc.kill()
        
    def stop(self):
        if self.is_stopped():
            return self.proc.returncode
        # first try SIGINT
        self.close()
        self.wait(self.timeout_close)
        if self.is_stopped():
            return self.proc.returncode
        # then try SIGTERM
        self.terminate()
        self.wait(self.timeout_terminate)
        if self.is_stopped():
            return self.proc.returncode
        # finally just kill it
        self.kill()
        return self.poll()
    
    @property
    def pid(self):
        return self.proc.pid
    @property
    def returncode(self):
        return self.proc.returncode


#==============================================================================#
class DjangoCommand(Process):
    def __init__(self, name, args, log=None, loglevel=None, env=None):
        assert DEFAULT_SETTINGS is not None
        settings = '--settings={0}'.format(DEFAULT_SETTINGS)
        pypath = '--pythonpath={0}'.format(DEFAULT_PYPATH)
        args = [DEFAULT_CMDBASE, name] + args
        if log:
            args.extend(['-f','{0}'.format(log)])
        if loglevel:
            args.extend(['-l','{0}'.format(loglevel)])
        args.extend([settings, pypath])  # settings has to come after other arguments
        
        super(DjangoCommand, self).__init__(args, env=env)
        
        
class DjCeleryd(DjangoCommand):
    timeout_close = 2.0
    def __init__(self, events=True, beat=False, hostname='', **kwargs):
        events = ['-E'] if events else []
        beat = ['-B'] if beat else []
        hostname = ['-n', hostname] if hostname else []
        args = events + beat + hostname
        super(DjCeleryd, self).__init__('celeryd', args, **kwargs)


class CMRun(DjangoCommand):
    timeout_close = 4.0
    def __init__(self, freq=0.1, **kwargs):
        freq = ['--frequency={0}'.format(freq)] if freq else []
        args = freq
        super(CMRun, self).__init__('cmrun', args, **kwargs)


#==============================================================================#
class ProcessSequence(object):
    """ Class that owns processes and destroys them in reverse order of their 
        creation.
    """
    def __init__(self):
        self.processes = []
        self.procmap = {}
        self.is_closed = False
        
    def add(self, procname, proctype, *args, **kwargs):
        assert self.is_closed == False
        assert len(self.processes) == len(self.procmap)
        try:
            if procname in self.procmap:
                raise RuntimeError('Process already exists by the name.')
            print 'ProcSeq: Launching {0}...'.format(procname)
            process = proctype(*args, **kwargs)
        except Exception:
            # close any prior processes
            print 'ProcSeq: Error while launching {0}.'.format(procname)
            self.close()
            raise
        self.processes.append((procname,process))
        self.procmap[procname] = process
        
    def __getitem__(self, name):
        return self.procmap[name]
        
    def close(self, procname=None):
        if procname:
            self._close_named_proc(procname)
        else:
            self._close_all_procs()
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        
    def _close_named_proc(self, procname):
        for i,(name,p) in enumerate(self.processes):
            if name==procname:
                break
        else:
            raise RuntimeError('Process {0} does not exist.'.format(procname))
        name,proc = self.processes.pop(i)
        assert name==procname
        if proc and not proc.is_stopped():
            print 'ProcSeq: Terminating {0}...'.format(name)
            proc.close()
            proc.wait()
    
    def _close_all_procs(self):
        exc_type = None
        while self.processes:
            try:
                name, proc = self.processes.pop()
                if proc and not proc.is_stopped():
                    print 'ProcSeq: Terminating {0}...'.format(name)
                    proc.close()
                    proc.wait()
            except Exception:
                import traceback, sys
                traceback.print_exc()
                exc_type, exc_val, exc_tb = sys.exc_info()
        if exc_type:
            raise exc_type(exc_val)


#==============================================================================#
    
    
    
    
    
            


