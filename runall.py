import subprocess
import time

from runall_config import process_arguments
    
class ProcessSet(object):
    def __init__(self, procsargs, init_delay=1.0):
        print 'ProcessSet: Starting processes...'
        self.procs = []
        try:
            for i,args in enumerate(procsargs):
                print 'ProcessSet: Starting process #{0}'.format(i+1)
                proc = subprocess.Popen(args)
                time.sleep(init_delay)
                self.procs.append(proc)
        except:
            self.terminate()
            raise
        
        if any(proc.poll() for proc in self.procs):
            self.terminate()
            raise RuntimeError("A process failed during initialization.")
        print 'ProcessSet: Processes started successfully...'
                    
    def __len__(self):
        return len(self.procs)
        
    def all_stopped(self):
        """Return True if all processes poll() methods return true.  In other 
           words, if they are all stopped.
        """
        return all(p.poll() for p in self.procs)
        
    def all_running(self):
        return not any(p.poll() for p in self.procs)
        
    def terminate(self):
        print 'ProcessSet: Terminating processes...'
        for proc in self.procs:
            if not proc.poll():
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
                if not proc.poll():
                    try:
                        proc.kill()
                    except OSError:
                        # Ignore "No such process"
                        pass
                
    def loop(self, interval=1.0):
        print 'ProcessSet: Entering loop...'
        try:
            while self.all_running():
                time.sleep(1.0)
                
        except:
            print 'ProcessSet: Leaving loop on exception...'
            self.terminate()
            raise
            
        print 'ProcessSet: Leaving loop normally...'
        self.terminate()
        
    def cleanup(self, waittime=2.0):
        print 'ProcessSet: Cleaning up...'
        i = 0
        while i<10 and not self.all_stopped():
            self.terminate()
            time.sleep(0.5)
            i+=1
        print 'ProcessSet: Allowing extra time for processes to stop before killing them...'
        time.sleep(2.0)
        self.kill()
        time.sleep(waittime)

           
def main():
    ps = ProcessSet(process_arguments)
    try:
        ps.loop()
    except:
        pass
    ps.cleanup(waittime=4.0)
    print 'ProcessSet: Completed!'


main()
