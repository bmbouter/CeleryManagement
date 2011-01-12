import datetime
import socket  # for socket.timeout exception

from celery.app import app_or_default

from celerymanagementapp.policy.manager import Registry, TaskSettingsManager
from celerymanagementapp.policy.signals import Receiver

#==============================================================================#
MIN_LOOP_SLEEP_TIME = 30  # seconds
MAX_LOOP_SLEEP_TIME = 60*2  # seconds

class PolicyMain(object):
    def __init__(self, connection, app=None):
        print 'cmrun: Starting PolicyMain...'
        self.task_settings = TaskSettingsManager()
        self.event_receiver = Receiver(connection, app=app)
        self.registry = Registry()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()
        
    def cleanup(self):
        print 'cmrun: PolicyMain.cleanup()...'
        self.registry.close()
        self.task_settings.cleanup()
        print 'cmrun: PolicyMain.cleanup()... complete.'
        
    def loop(self):
        print 'cmrun: Starting PolicyMain loop...'
        try:
            while True:
                self.refresh_registry()
                sleeptime = self.run_ready_policies()
                sleeptime = max(sleeptime,MIN_LOOP_SLEEP_TIME)
                print 'cmrun: Sleeping for {0:.2f} seconds.'.format(sleeptime)
                self.handle_messages(sleeptime)
        finally:
            print 'cmrun: Exiting PolicyMain loop.'
        
    def refresh_registry(self):
        self.registry.refresh()
        
    def handle_messages(self, sleeptime):
        try:
            self.event_receiver.capture(limit=None, timeout=sleeptime)
        except socket.timeout:
            pass
        
    def run_ready_policies(self):
        print 'cmrun: Running ready policies...'
        now = datetime.datetime.now()
        modified_ids = []
        run_deltas = []
        # TODO: put try block on inside of loop, so we can continue with other 
        # policies if an exception is thrown.
        try:
            for entry in self.registry:
                is_due, next_run_delta = entry.is_due()
                if is_due:
                    self.run_policy(entry.policy)
                    entry.set_last_run_time(now)
                    modified_ids.append(entry.policy.id)
                run_deltas.append(next_run_delta)
        finally:
            print 'cmrun: Finished running ready policies.'
            now = datetime.datetime.now()
            for id in modified_ids:
                self.registry.save(id, now)
        return min(run_deltas+[MAX_LOOP_SLEEP_TIME])
            
    def run_policy(self, policyobj):
        print 'cmrun: Running policy "{0}"'.format(policyobj.name)
        if policyobj.run_condition():
            policyobj.run_apply()
        
        
#==============================================================================#
def policy_main(app=None):
    print 'cmrun: Loading policy manager...'
    app = app_or_default(app)
    conn = app.broker_connection()
    try:
        try:
            with PolicyMain(conn) as pmain:
                pmain.loop()
        except KeyboardInterrupt:
            raise SystemExit
    finally:
        #import traceback
        #traceback.print_exc()
        conn.close()
        print 'cmrun: Policy manager shut down.'
        
