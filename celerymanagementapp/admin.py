from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from djcelery.admin import TaskMonitor, fixedwidth

from celerymanagementapp.models import DispatchedTask

# class DispatchedTaskAdmin(TaskMonitor):
    # fieldsets = (
            # (None, {
                # "fields": ("state", "task_id", "name", "args", "kwargs",
                           # "eta", "runtime", "worker", "tstamp", "waittime", "sent"),
                # "classes": ("extrapretty", ),
            # }),
            # ("Details", {
                # "classes": ("collapse", "extrapretty"),
                # "fields": ("result", "traceback", "expires"),
            # }),
    # )
    
    # list_display = TaskMonitor.list_display + (
                    # 'waittime',
                    # 'sent')
                    
#    list_display = ('name','open_date','close_date')
    
#admin.site.register(DispatchedTask, DispatchedTaskAdmin)
admin.site.register(DispatchedTask)
