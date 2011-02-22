import datetime
import socket
import random
import string

import libcloud.types
import libcloud.providers

from django.db import models
from django.utils.translation import ugettext_lazy as _

from djcelery.models import WorkerState, TaskState, TASK_STATE_CHOICES
from djcelery.managers import TaskStateManager

from django.conf import settings
from django.core.files.storage import FileSystemStorage
fs = FileSystemStorage(location=settings.SECURE_UPLOADS)

from celerymanagementapp.ssh_tools import NodeUtil

#==============================================================================#
#class DefinedTask(models.Model):
#    """Represents a task class, that is, a subclass of celery.task.base.Task, 
#       that has been registered within Celery.  Since the @task() decorator 
#       turns a function into a task class, this model also includes them.
#    """
#    name = models.CharField(max_length=512, editable=False)  # is 512 ok?
    
#==============================================================================#

class DispatchedTask(models.Model):
    """A Celery Task that has been sent."""
    name =      models.CharField(_(u"name"), max_length=200, null=True, 
                                 db_index=True)
    state =     models.CharField(_(u"state"), max_length=64, 
                                 choices=TASK_STATE_CHOICES)
    task_id =   models.CharField(_(u"UUID"), max_length=36, unique=True)
    worker =    models.ForeignKey(WorkerState, null=True, 
                                  verbose_name=_("worker"))
    
    runtime =   models.FloatField(_(u"execution time"), null=True, 
                                  help_text=_(u"in seconds if task successful"))
    waittime =  models.FloatField(_(u"wait time"), null=True)
    totaltime = models.FloatField(_(u"total time"), null=True)
    
    tstamp =    models.DateTimeField(_(u"last event received at"), 
                                     db_index=True)
    sent =      models.DateTimeField(_(u"sent time"), null=True)
    received =  models.DateTimeField(_(u"received time"), null=True)
    started =   models.DateTimeField(_(u"started time"), null=True)
    succeeded = models.DateTimeField(_(u"succeeded time"), null=True)
    failed =    models.DateTimeField(_(u"failed time"), null=True)
    
    routing_key = models.CharField(_(u"routing key"), max_length=200, 
                                   null=True)
    expires =   models.DateTimeField(_(u"expires"), null=True)
    result =    models.TextField(_(u"result"), null=True)
    retries =   models.IntegerField(_(u"number of retries"), default=0)
    
    eta =       models.DateTimeField(_(u"ETA"), null=True, 
                                     help_text=u"date to execute")
    
    hidden =    models.BooleanField(editable=False, default=False)
    
    objects = TaskStateManager()
    
    class Meta:
        """Model meta-data."""
        verbose_name = _(u"Dispatched Task")
        verbose_name_plural = _(u"tasks")
        get_latest_by = "tstamp"
        ordering = ["-tstamp"]

class AbstractWorkerNode(models.Model):
    """ An abstract class containing common attributes used by Provider and 
        WorkerNode. """
    celeryd_username = models.CharField(_(u"username"),
            max_length=64)
    ssh_key = models.FileField("SSH key", upload_to='sshkeys', storage=fs)
    celeryd_start_cmd = models.TextField(_(u"commands to start celeryd"),
            max_length=1024)
    celeryd_stop_cmd = models.TextField(_(u"commands to stop celeryd"),
            max_length=1024)
    celeryd_status_cmd = models.TextField(
            _(u"commands to report celeryd status"), max_length=1024)

    class Meta:
        abstract = True

class OutOfBandWorkerNode(AbstractWorkerNode):
    """An out-of-band Worker Node"""
    ip = models.IPAddressField(_(u"IP address"), unique=True)

    def __unicode__(self):
        return self.ip

    def clean(self):
        try:
            socket.inet_aton(self.ip)
        except:
            from django.core.exceptions import ValidationError
            raise ValidationError("%s is not a valid IP address" % self.ip)
        ssh = self._get_SSH_Object()
        if not ssh.ssh_avail():
            from django.core.exceptions import ValidationError
            raise ValidationError("SSH does not seem to be available on %s" 
                                  % self.ip)

    def _get_SSH_Object(self):
        return NodeUtil(self.ip, settings.SECURE_UPLOADS + str(self.ssh_key),
            self.celeryd_username)

    def celeryd_start(self):
        """SSH's to the Node and runs the celeryd_start commands"""
        ssh = self._get_SSH_Object()
        return ssh.ssh_run_command(self.celeryd_start_cmd.split(' '))

    def celeryd_stop(self):
        """SSH's to the Node and runs the celeryd_stop commands"""
        ssh = self._get_SSH_Object()
        return ssh.ssh_run_command(self.celeryd_stop_cmd.split(' '))

    def celeryd_status(self):
        """SSH's to the Node and runs the celeryd_stop commands"""
        ssh = self._get_SSH_Object()
        return ssh.ssh_run_command(self.celeryd_status_cmd.split(' '))

    def is_celeryd_running(self):
        output = self.celeryd_status()
        return output.strip('\n').isdigit()
        
class Provider(AbstractWorkerNode):
    """Represents a infrastructure provider for libcloud"""

    PROVIDER_CHOICES = (
        ('DREAMHOST', 'DreamHost'),
        ('DUMMY', 'Dummy Driver'),
        ('EC2_US_EAST', 'Amazon EC2 US East'),
        ('EC2_US_WEST', 'Amazon EC2 US West'),
        ('EC2_EU_WEST', 'Amazon Europe West'),
        ('EC2_AP_SOUTHEAST', 'Amazon Asia Pacific Southeast'),
        ('ECP', 'Enomaly ECP'),
        ('ELASTICHOSTS_UK1', 'ElasticHosts UK 1'),
        ('ELASTICHOSTS_UK2', 'ElasticHosts UK 2'),
        ('ELASTICHOSTS_US1', 'ElasticHosts US 1'),
        ('GOGRID', 'GoGrid'),
        ('IBM', 'IBM Developer Cloud'),
        ('LINODE', 'Linode'),
        ('OPENNEBULA', 'OpenNebula'),
        ('RACKSPACE', 'Rackspace'),
        ('RIMUHOSTING', 'RimuHosting'),
        ('SLICEHOST', 'Slicehost'),
        ('SOFTLAYER', 'Softlayer'),
        ('VOXEL', 'Voxel VoxCloud'),
        ('VPSNET', 'VPS.net'),
    )

    provider_user_id = models.CharField(_(u"Provider user id"),
            max_length=128, blank=True)
    provider_key = models.CharField(_(u"Provider key"),
            max_length=128)
    provider_name = models.CharField(_('provider'), max_length=32, 
                                     choices=PROVIDER_CHOICES)
    image_id = models.CharField(_(u"image id"),
            max_length=64)

    def are_credentials_valid(self):
        """Returns true if Provider credentials are valid.  False otherwise."""
        try:
            conn = self.conn
            return True
        except (libcloud.types.InvalidCredsError, AttributeError):
            return False

    def clean(self):
        if not self.are_credentials_valid():
            from django.core.exceptions import ValidationError
            raise ValidationError("Invalid Provider Credentials")
        if self._get_image_obj() is None:
            from django.core.exceptions import ValidationError
            raise ValidationError("Image ID is not valid")

    def __unicode__(self):
        return self.provider_name

    def _get_image_obj(self):
        """ Returns an object of type libcloud.base.NodeImage looked up by id 
            or name """
        images = self.conn.list_images()
        for image in images:
            if self.image_id == unicode(image.id):
                return image

    @property
    def sizes(self):
        """Returns a list of libcloud.base.NodeSize objects"""
        return self.conn.list_sizes()

    @property
    def conn(self):
        """Returns a libcloud driver connection

        This method will raise a libcloud.types.InvalidCredsError if the
        credentials are not valid.  Anytime this method is called, it should be
        wrapped in an except statement which should handle cases when the
        credentials are not correct.

        """
        p = getattr(libcloud.types.Provider, self.provider_name)
        Driver = libcloud.providers.get_driver(p)
        try:
            return Driver(self.provider_user_id, secret=self.provider_key)
        except TypeError as type_error:
            errmsg = "__init__() got an unexpected keyword argument 'secret'"
            if type_error.args[0] == errmsg:
                # Libcloud doesn't have consistant interfaces so some objects 
                # that inherit from Driver need to only take one parameter.  
                # This code is designed to detect and workaround this error.
                return Driver(self.provider_user_id)

    def create_vm(self):
        """Creates and starts a VM on Provider"""
        chars = string.letters + string.digits
        while True:
            random_string = ''.join([random.choice(chars)for i in range(8)])
            vm_name = 'celerydworker%s' % random_string
            node_image = self._get_image_obj()
            try:
                new_vm = self.conn.create_node(name=vm_name, image=node_image, 
                                               size=self.sizes[0]) 
                break
            except Exception as e:
                if 'Server name already in use' in e.args[0]:
                    pass
        in_band_worker_node = InBandWorkerNode(instance_id=new_vm.id, 
                                               provider=self)
        in_band_worker_node.save()
        start_celeyrd_on_vm(in_band_worker_node.pk)
        return in_band_worker_node

class InBandWorkerNode(models.Model):
    instance_id = models.CharField(_(u"instance id"),
            max_length=64)
    provider = models.ForeignKey('celerymanagementapp.Provider')

    def __unicode__(self):
        return 'Image %s on %s' % (self.instance_id, 
                                   self.provider.provider_name)

    def _get_node_obj(self):
        """Returns an object of type libcloud.base.Node looked up by id"""
        nodes = self.provider.conn.list_nodes()
        for node in nodes:
            if self.instance_id == node.id:
                return node

    def delete(self, *args, **kwargs):
        """Delete's the running virtual machine"""
        node = self._get_node_obj()
        self.provider.conn.destroy_node(node)
        super(InBandWorkerNode, self).delete(*args, **kwargs)

    def _get_SSH_Object(self):
        node = self._get_node_obj()
        return NodeUtil(node.public_ip[0], 
                        settings.SECURE_UPLOADS + str(self.provider.ssh_key), 
                        self.provider.celeryd_username)

    def celeryd_start(self):
        """SSH's to the Node and runs the celeryd_start commands"""
        ssh = self._get_SSH_Object()
        return ssh.ssh_run_command(self.provider.celeryd_start_cmd.split(' '))

    def celeryd_stop(self):
        """SSH's to the Node and runs the celeryd_stop commands"""
        ssh = self._get_SSH_Object()
        return ssh.ssh_run_command(self.provider.celeryd_stop_cmd.split(' '))

    def celeryd_status(self):
        """SSH's to the Node and runs the celeryd_stop commands"""
        ssh = self._get_SSH_Object()
        return ssh.ssh_run_command(self.provider.celeryd_status_cmd.split(' '))

    def is_celeryd_running(self):
        output = self.celeryd_status()
        return output.strip('\n').isdigit()

        
class RegisteredTaskType(models.Model):
    """ A task type that has been registered with a worker.  This is *not* the 
        same as a DefinedTask.
    """
    name =      models.CharField(_(u"name"), max_length=200)
    # The worker that the task is registered with.
    worker =    models.CharField(_(u"worker"), max_length=200)
    modified =  models.DateTimeField(_(u"modified"), auto_now=True)
    
    
    class Meta:
        """Model meta-data."""
        unique_together = (('name', 'worker'), )
        
    @staticmethod
    def clear_tasks(workername):
        """Erase tasks registered with the given worker."""
        RegisteredTaskType.objects.filter(worker=workername).delete()
        
    @staticmethod
    def add_task(taskname, workername):
        """Add a new task registered with the given worker."""
        RegisteredTaskType.objects.get_or_create(name=taskname, 
                                                 worker=workername)
        
    def __unicode__(self):
        return u'{0} --- {1}'.format(self.name, self.worker)
        
        
class TaskDemoGroup(models.Model):
    uuid =              models.CharField(max_length=32, db_index=True, 
                                         unique=True)
    name =              models.CharField(max_length=200)
    ##launcher_uuid =     models.CharField(max_length=36, unique=True)
    elapsed =           models.FloatField(default=-1.0)
    tasks_sent =        models.IntegerField(default=-1)
    completed =         models.BooleanField(default=False)
    errors_on_send =    models.IntegerField(default=-1)
    errors_on_result =  models.IntegerField(default=-1)
    timestamp =         models.DateTimeField()
    
    requested_rate =    models.FloatField(default=0.0)
    requested_runfor =  models.FloatField(default=0.0)
    requested_args =    models.TextField(default="")
    requested_kwargs =  models.TextField(default="")
    requested_options = models.TextField(default="")
    
    def __unicode__(self):
        return u"<{0}> {1} {2}".format(self.uuid, self.name, self.timestamp)


class PolicyModel(models.Model):
    """ Model for Policy objects. """
    name =          models.CharField(max_length=100, null=False, unique=True)
    modified =      models.DateTimeField(null=True, default=None, blank=True)
    enabled =       models.BooleanField(default=False)
    last_run_time = models.DateTimeField(null=True, default=None, blank=True)
    source =        models.TextField(default="")
    # add field which keeps error information
    
    def __unicode__(self):
        return u"<{0}>  last run: {1}  enabled: {2}".format(self.name, 
                                                            self.last_run_time, 
                                                            self.enabled)
        
    def save(self, *args, **kwargs):
        # convert Windows newlines to Unix newlines
        self.source = self.source.replace('\r\n', '\n')
        super(PolicyModel, self).save(*args, **kwargs)



class TestModel(models.Model):
    """A model solely for use in testing."""
    date =      models.DateField(null=True)
    datetime =  models.DateTimeField(null=True)
    floatval =  models.FloatField()
    intval =    models.IntegerField()
    charval =   models.CharField(max_length=128)
    enumval =   models.CharField(max_length=1, 
                                 choices=(('A', 'A'), ('B', 'B'),
                                          ('C', 'C'), ('D', 'D'))
                                )
