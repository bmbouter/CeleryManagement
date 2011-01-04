import datetime
import socket

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
    
    tstamp =    models.DateTimeField(_(u"last event received at"), db_index=True)
    sent =      models.DateTimeField(_(u"sent time"), null=True)
    received =  models.DateTimeField(_(u"received time"), null=True)
    started =   models.DateTimeField(_(u"started time"), null=True)
    succeeded = models.DateTimeField(_(u"succeeded time"), null=True)
    failed =    models.DateTimeField(_(u"failed time"), null=True)
    
    routing_key = models.CharField(_(u"routing key"), max_length=200, null=True)
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

class OutOfBandWorkerNode(models.Model):
    """An out-of-band Worker Node"""
    ip = models.IPAddressField(_(u"IP address"), unique=True)
    username = models.CharField(_(u"username"),
            max_length=64)
    ssh_key = models.FileField("SSH key", upload_to='sshkeys', storage=fs)
    celeryd_start_cmd = models.TextField(_(u"commands to start celeryd"),
            max_length=1024)
    celeryd_stop_cmd = models.TextField(_(u"commands to stop celeryd"),
            max_length=1024)
    celeryd_status_cmd = models.TextField(
            _(u"commands to report celeryd status"), max_length=1024)
    active = models.BooleanField(_(u"currently active"), default=True)

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
            raise ValidationError("SSH does not seem to be available on %s" % self.ip)

    def _get_SSH_Object(self):
        return NodeUtil(self.ip, settings.SECURE_UPLOADS + str(self.ssh_key),
            self.username)

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
        
class Provider(models.Model):
    """Represents a infrastructure provider for libcloud"""

    PROVIDER_CHOICES = (
        ('dreamhost', 'DreamHost'),
        ('dummy', 'Dummy Driver'),
        ('ec2', 'Amazon EC2'),
        ('ecp', 'Enomaly ECP'),
        ('elastichosts', 'ElasticHosts'),
        ('gogrid', 'GoGrid'),
        ('ibm_sbc', 'IBM Developer Cloud'),
        ('linode', 'Linode'),
        ('opennebula', 'OpenNebula'),
        ('rackspace', 'Rackspace'),
        ('rimuhosting', 'RimuHosting'),
        ('slicehost', 'Slicehost'),
        ('softlayer', 'Softlayer'),
        ('vcloud', 'VMware vCloud'),
        ('voxel', 'Voxel VoxCloud'),
        ('vpsnet', 'VPS.net'),
    )

    username = models.CharField(_(u"username"),
            max_length=128)
    password = models.CharField(_(u"password"),
            max_length=128)
    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES)
    image_id = models.CharField(_(u"image id"),
            max_length=64)

    def clean(self):
        import pdb;pdb.set_trace()
        from django.core.exceptions import ValidationError
        raise ValidationError("Invalid Provider Credentials")

    def __unicode__(self):
        return self.driver

    @property
    def conn(prov):
        """Returns a libcloud driver connection"""
        provider = libcloud.types.Provider.__getattr__[self.provider]
        Driver = libcloud.providers.get_driver(provider)
        return Driver(self.username, self.password)

    def create_vm(self):
        """Creates and starts a VM on Provider"""
        new_vm = self.conn.create_node(image=self.image_id, size=sizes[0]) 
        return InBandWorkerNode(instance_id=new_vm.instance_id, provider=self)

class InBandWorkerNode(OutOfBandWorkerNode):
    instance_id = models.CharField(_(u"instance id"),
            max_length=64)
    provider = models.ForeignKey('celerymanagementapp.Provider')

    def __unicode__(self):
        return '%s on %s' % (self.ip, self.provider.name)

    def delete(self, *args, **kwargs):
        """Delete's the running virtual machine"""
        self.provider.conn.destroy()
        super(Blog, self).delete(*args, **kwargs)

# class DefinedTask(models.Model):
    # """A task type that has been defined."""
    # name =      models.CharField(_(u"name"), max_length=200, null=True, 
                                 # db_index=True)
    # worker =    models.CharField(_(u"worker"), max_length=200, null=True, 
                                 # db_index=True)
        
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
        unique_together = (('name','worker'),)
        
    @staticmethod
    def clear_tasks(workername):
        """Erase tasks registered with the given worker."""
        RegisteredTaskType.objects.filter(worker=workername).delete()
        
    @staticmethod
    def add_task(taskname, workername):
        """Add a new task registered with the given worker."""
        RegisteredTaskType.objects.get_or_create(name=taskname, worker=workername)
        
    def __unicode__(self):
        return u'{0} --- {1}'.format(self.name, self.worker)
        
        
class TaskDemoGroup(models.Model):
    uuid =              models.CharField(max_length=32, db_index=True, unique=True)
    name =              models.CharField(max_length=200)
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
    modified =      models.DateTimeField(null=True)
    enabled =       models.BooleanField(default=False)
    last_run_time = models.DateTimeField(null=True)
    source =        models.TextField(default="")
    
    def __unicode__(self):
        return u"<{0}>  last run: {1}  enabled: {2}".format(self.name, self.last_run_time, self.enabled)



class TestModel(models.Model):
    """A model solely for use in testing."""
    date =      models.DateField(null=True)
    floatval =  models.FloatField()
    intval =    models.IntegerField()
    charval =   models.CharField(max_length=128)
    enumval =   models.CharField(max_length=1, 
                                 choices=(('A','A'),('B','B'),
                                          ('C','C'),('D','D'))
                                )
