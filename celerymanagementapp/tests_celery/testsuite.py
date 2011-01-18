from celerymanagementapp.testutil.unittest import unittest
from celerymanagementapp.testutil import process

# Disable Nose test autodiscovery for this module.
__test__ = False

#==============================================================================#
class ScopedTestSuite(unittest.TestSuite):
    def __init__(self):
        super(ScopedTestSuite, self).__init__()
        
    def setUpSuite(self):
        pass
    def tearDownSuite(self):
        pass
    
    def run(self, result):
        self.setUpSuite()
        try:
            super(ScopedTestSuite, self).run(result)
        finally:
            self.tearDownSuite()
        return result
        
    # Overriding TestSuite _wrapped_run() method since the run() method is 
    # *not* called except by the top-level suite.  This issue has been fixed on 
    # the Python 2.7 maintenance branch (rev 86104).
    def _wrapped_run(self, result, debug=False):
        self.setUpSuite()
        try:
            super(ScopedTestSuite, self)._wrapped_run(result, debug)
        finally:
            self.tearDownSuite()

#==============================================================================#
class CommonProcSuite(ScopedTestSuite):
    def __init__(self):
        super(ScopedTestSuite, self).__init__()
        self.celeryd = None
        self.cmrun = None
    
    def setUpSuite(self):
        try:
            print 'Launching celeryd...'
            self.celeryd = process.DjCeleryd(log='celeryd.log.txt')
            print 'Launching cmrun...'
            self.cmrun = process.CMRun(freq=0.1, log='celeryev.log.txt')
        except Exception:
            print 'Error encountered while starting celeryd and/or cmrun.'
            if self.celeryd and not self.celeryd.is_stopped():
                self.celeryd.close()
                self.celeryd.wait()
            if self.cmrun and not self.cmrun.is_stopped():
                self.cmrun.close()
                self.cmrun.wait()
            raise
        
    def tearDownSuite(self):
        print ''
        print 'Terminating cmrun...'
        self.cmrun.close()
        self.cmrun.wait()
        print 'Terminating celeryd...'
        self.celeryd.close()
        self.celeryd.wait()
    


#==============================================================================#



