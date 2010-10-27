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
        
    def poll(self):
        return any(p.poll() for p in self.procs)
        
    def terminate(self):
        print 'ProcessSet: Terminating processes...'
        for proc in self.procs:
            if not proc.poll():
                proc.terminate()
                
    def kill(self):
        if self.poll():
            print 'ProcessSet: Killing processes...'
            for proc in self.procs:
                if not proc.poll():
                    proc.kill()
                
    def loop(self, interval=1.0):
        print 'ProcessSet: Entering loop...'
        try:
            while not self.poll():
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
        while i<10 and self.poll():
            self.terminate()
            time.sleep(0.5)
            i+=1
        self.kill()
        print 'ProcessSet: Allowing extra time for processes to stop...'
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