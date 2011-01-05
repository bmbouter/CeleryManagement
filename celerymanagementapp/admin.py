from celery import states

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from djcelery.admin import TaskMonitor, fixedwidth

from celerymanagementapp.models import DispatchedTask, OutOfBandWorkerNode, Provider, InBandWorkerNode
from celerymanagementapp.models import RegisteredTaskType, TaskDemoGroup

# 'TASK_STATE_COLORS' and 'colored_state()' from djcelery.admin
TASK_STATE_COLORS = {states.SUCCESS: "green",
                     states.FAILURE: "red",
                     states.REVOKED: "magenta",
                     states.STARTED: "yellow",
                     states.RETRY: "orange",
                     "RECEIVED": "blue"}

def format_seconds(val, fracdigits=6):
    if val:
        return '{0:.{flen}f}'.format(val,flen=fracdigits)
    else:
        return ''
    
def display_field(name, allow_tags=False):
    def _inner(func):
        func.short_description = name
        func.allow_tags = allow_tags
        return func
    return _inner
    
@display_field('Runtime')
def runtime_field(obj):
    return format_seconds(obj.runtime, 6)
    
@display_field('Wait Time')
def waittime_field(obj):
    return format_seconds(obj.waittime, 2)
    
@display_field('Total Time')
def totaltime_field(obj):
    return format_seconds(obj.totaltime, 2)
    
@display_field('Name')
def name_field(obj):
    name = obj.name
    if len(name) > 20:
        head,sep,tail = name.rpartition('.')
        hlen = max(20 - len(tail), 8)
        head = head[:hlen]
        name = '{0}[.]{1}'.format(head,tail)
    return name
    
@display_field('State', allow_tags=True)
def colored_state_field(obj):
    color = TASK_STATE_COLORS.get(obj.state, "black")
    return """<b><span style="color: %s;">%s</span></b>""" % (color, obj.state)


class DispatchedTaskAdmin(admin.ModelAdmin):
    date_heirarchy = 'tstamp'
    list_display = ('task_id', name_field, colored_state_field, 'worker', 
                    'tstamp', runtime_field, waittime_field, totaltime_field, 
                    'routing_key')
    list_filter = ('name', 'state', 'worker', 'routing_key', 'tstamp')
    
class RegisteredTaskTypeAdmin(admin.ModelAdmin):
    list_display = ('worker','name','modified')
    list_filter = ('worker','name','modified')

class ProviderAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Provider Settings', {
            'fields': ('provider_name', 'provider_user_id', 'provider_key')
        }),
        ('Image Settings', {
            'fields': ('image_id', 'celeryd_username', 'ssh_key', 'celeryd_start_cmd', 'celeryd_stop_cmd', 'celeryd_status_cmd')
        }),
    )
    
admin.site.register(DispatchedTask, DispatchedTaskAdmin)
admin.site.register(OutOfBandWorkerNode)
admin.site.register(InBandWorkerNode)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(RegisteredTaskType, RegisteredTaskTypeAdmin)
admin.site.register(TaskDemoGroup)

