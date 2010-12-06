import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from djcelery.models import WorkerState, TaskState, TASK_STATE_CHOICES
from djcelery.managers import TaskStateManager

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
        verbose_name = _(u"task")
        verbose_name_plural = _(u"tasks")
        get_latest_by = "tstamp"
        ordering = ["-tstamp"]
    

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
