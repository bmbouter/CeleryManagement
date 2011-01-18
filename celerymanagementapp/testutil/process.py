import subprocess
import signal
import time

DEFAULT_CMDBASE = 'django-admin.py'
DEFAULT_PYPATH = '.'
DEFAULT_SETTINGS = None #'testcelery_settings'

WAIT_SLEEP_INTERVAL = 0.05


class TimeoutError(Exception):
    pass


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


class DjangoCommand(Process):
    def __init__(self, name, args, log=None, loglevel=None):
        assert DEFAULT_SETTINGS is not None
        settings = '--settings={0}'.format(DEFAULT_SETTINGS)
        pypath = '--pythonpath={0}'.format(DEFAULT_PYPATH)
        args = [DEFAULT_CMDBASE, name] + args
        if log:
            args.extend(['-f','{0}'.format(log)])
        if loglevel:
            args.extend(['-l','{0}'.format(log)])
        args.extend([settings, pypath])  # settings has to come after other arguments
        
        super(DjangoCommand, self).__init__(args)
        
        
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




