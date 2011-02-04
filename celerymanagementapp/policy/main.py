import datetime
import socket  # for socket.timeout exception

from celery.app import app_or_default
from celery.utils import LOG_LEVELS

from celerymanagementapp.policy.manager import Registry, TaskSettingsManager
from celerymanagementapp.policy.signals import Receiver
from celerymanagementapp.policy import util

#==============================================================================#
MIN_LOOP_SLEEP_TIME = 20  # seconds
MAX_LOOP_SLEEP_TIME = 45  # seconds

class PolicyMain(object):
    """ The main Policy application class.  Policies are actually executed 
        here. 
    """
    def __init__(self, connection, logger, app=None):
        ##print 'cmrun: Starting PolicyMain...'
        self.logger = logger
        self.logger.debug('Starting PolicyMain...')
        self.task_settings = TaskSettingsManager(logger)
        self.event_receiver = Receiver(connection, logger, app=app)
        self.registry = Registry(logger)
        self.logger.debug('PolicyMain initialized.')
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()
        
    def cleanup(self):
        ##print 'cmrun: PolicyMain.cleanup()...'
        self.logger.debug('PolicyMain.cleanup()...')
        
        self.registry.close()
        self.task_settings.cleanup()
        
        ##print 'cmrun: PolicyMain.cleanup()... complete.'
        self.logger.debug('PolicyMain.cleanup()... complete.')
        
    def loop(self):
        """ The main policy-manager loop. """
        ##print 'cmrun: Starting PolicyMain loop...'
        self.logger.debug('Starting PolicyMain loop...')
        try:
            while True:
                self.refresh_registry()
                sleeptime = self.run_ready_policies()
                sleeptime = max(sleeptime,MIN_LOOP_SLEEP_TIME)
                ##print 'cmrun: Sleeping for {0:.2f} seconds.'.format(sleeptime)
                self.logger.debug(
                    'Sleeping for {0:.2f} seconds.'.format(sleeptime))
                self.handle_messages(sleeptime)
        finally:
            ##print 'cmrun: Exiting PolicyMain loop.'
            self.logger.debug('Exiting PolicyMain loop.')
        
    def refresh_registry(self):
        self.registry.refresh()
        
    def handle_messages(self, sleeptime):
        """ Handles Celery events until sleeptime seconds has elapsed or an 
            exception is thrown. 
        """
        try:
            self.event_receiver.capture(limit=None, timeout=sleeptime)
        except socket.timeout:
            pass
        
    def run_ready_policies(self):
        """ Look for Policies that may be due to be run, and try to run 
            them. 
        """
        start = datetime.datetime.now()
        modified_ids = []
        run_deltas = []
        
        # Only run policies if there are workers.
        if util.get_all_worker_names():
            self.logger.debug('Running ready policies...')
            try:
                for entry in self.registry:
                    was_run, next_run_delta = self.maybe_run_policy(entry)
                    if was_run:
                        entry.set_last_run_time(start)
                        modified_ids.append(entry.policy.id)
                    if next_run_delta:
                        run_deltas.append(next_run_delta)
            finally:
                self.logger.debug('Finished running ready policies.')
                now = datetime.datetime.now()
                for id in modified_ids:
                    self.registry.save(id, now)
        else:
            msg = 'Not running policies -- no workers are available.'
            self.logger.warn(msg)
            run_deltas.append(MIN_LOOP_SLEEP_TIME)
        
        delta = datetime.datetime.now() - start
        secs = delta.seconds + delta.microseconds/1000000.
        self.logger.debug(
            'Ran {0} policies in {1} seconds'.format(len(modified_ids), secs))
        
        return min(run_deltas+[MAX_LOOP_SLEEP_TIME])
        
    def maybe_run_policy(self, entry):
        """ Check to see if a Policy is due to be run, and if so, run it.  
        
            Exceptions will not propagate from here.  This prevents an 
            exception from one Policy from denying others the chance to run.
        """
        was_run = False
        try:
            is_due, next_run_delta = entry.is_due()
            if is_due:
                self.run_policy(entry.policy)
                was_run = True
        except (KeyboardInterrupt, SystemExit):
            # Do not ignore these exceptions.
            raise
        except Exception:
            import traceback
            msg = 'Exception occurred while running policy: ' 
            msg += '{0}\n'.format(entry.policy.name)
            msg += 'The following is the traceback:\n'
            msg += traceback.format_exc()
            # Print exception traceback to the log so at least the user knows it 
            # occurred.
            self.logger.error(msg)
            next_run_delta = 0
        return (was_run, next_run_delta)
            
    def run_policy(self, policyobj):
        """ Run the given Policy.
            
            First, the Policy's condition section is run.  If that evaluates to 
            true, then the apply section is run.
        """
        name = policyobj.name
        self.logger.debug('Checking policy {0} (condition)'.format(name))
        if policyobj.run_condition():
            self.logger.info('Running policy {0} (apply)'.format(name))
            policyobj.run_apply()
        
        
#==============================================================================#
def policy_main(app=None, loglevel=0, logfile=None):
    """ Policy manager entry-point function. """
    ##print 'cmrun: Loading policy manager...'
    import logging
    import sys
    app = app_or_default(app)
    if not isinstance(loglevel, int):
        loglevel = LOG_LEVELS[loglevel.upper()]
    logger = app.log.setup_logger(loglevel=loglevel,
                                  logfile=logfile,
                                  name="cm.policy")
    orig_ios = (sys.stdout, sys.stderr)
    ##app.log.redirect_stdouts_to_logger(logger, loglevel=logging.INFO)
    logger.info('-> cm.policy: Loading policy manager...')
    conn = app.broker_connection()
    try:
        try:
            with PolicyMain(conn, logger, app=app) as pmain:
                pmain.loop()
        except KeyboardInterrupt:
            raise SystemExit
        except SystemExit:
            raise
        except Exception:
            import traceback
            tb = traceback.format_exc()
            logger.error('\n'+tb)
            raise
    finally:
        #import traceback
        #traceback.print_exc()
        conn.close()
        logger.info('-> cm.policy: Policy manager shut down.')
        sys.stdout, sys.stderr = orig_ios
        ##print 'cmrun: Policy manager shut down.'
        
