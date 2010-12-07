import datetime
from django.conf.urls.defaults import *
from django.conf import settings


DATEMIN = r'(?P<datemin>\d{4}-\d{2}-\d{2})'
DATEMAX = r'(?P<datemax>\d{4}-\d{2}-\d{2})'
# accepts:  date_date   or   date_   or   _date
DATERANGE1 = '(?:'+DATEMIN+'_'+DATEMAX+'?)'
DATERANGE2 = '(?:_'+DATEMAX+')'

USERNAME = r'(?P<username>[a-zA-Z0-9]+)'##JOBID = r'(?:_job_(?P<jobid>[0-9]+))'

urlpatterns = patterns('celerymanagementapp',
    (r'^view/tasks/$', 'views.view_defined_tasks'),
    (r'^view/throughputs/$', 'views.view_throughputs'),
    (r'^view/throughputs/(?P<taskname>[-\w\d_.]+)/$', 'views.view_throughputs'),
    
    (r'^visualize/throughputs/$', 'views.visualize_throughput'),
    (r'^visualize/throughputs/(?P<taskname>[-\w\d_.]+)/$', 'views.visualize_throughput'),
    
    (r'^visualize/runtimes/$', 'views.visualize_runtimes'),
    (r'^visualize/runtimes/(?P<taskname>[-\w\d_.]+)/$', 'views.visualize_runtimes'),
    (r'^visualize/runtimes/(?P<taskname>[-\w\d_.]+)/(?P<bin_count>[\d]+)/$', 'views.visualize_runtimes'),
    (r'^visualize/runtimes/(?P<taskname>[-\w\d_.]+)/(?P<bin_count>[\d]+)/(?P<bin_size>[\d.]+)/$', 'views.visualize_runtimes'),
    (r'^visualize/runtimes/(?P<taskname>[-\w\d_.]+)/(?P<runtime_min>[\d.]+)/(?P<bin_count>[\d]+)/(?P<bin_size>[\d.]+)/$', 'views.visualize_runtimes'),
    
    (r'^view/dispatched_tasks/$', 'views.view_dispatched_tasks'),
    (r'^view/dispatched_tasks/(?P<taskname>[-\w\d_.]+)/$', 'views.view_dispatched_tasks'),
    
    (r'^test/$', 'views.test_view'),
)

# Data retrieval URLs
urlpatterns += patterns('celerymanagementapp',    
    (r'^xy_query/dispatched_tasks/$', 'dataviews.task_xy_dataview'),
    
    # For the following urls, the *name* may be a task or worker name (whichever 
    # is appropriate) or 'all' which returns information on all items.
    # General url pattern: worker/NAME/...
    (r'^worker/all/list/$', 'dataviews.worker_list_dataview'),
    (r'^worker/(?P<name>[-\w\d_.]+)/subprocess/count/$', 'dataviews.worker_subprocesses_dataview'),
    
    # General url pattern: task/NAME/...
    (r'^task/all/list/$', 'dataviews.definedtask_list_dataview'),
    (r'^task/(?P<name>[-\w\d_.]+)/dispatched/pending/count/$', 'dataviews.pending_task_count_dataview'),
    (r'^task/(?P<name>[-\w\d_.]+)/dispatched/byworker/count/$', 'dataviews.tasks_per_worker_dataview'),
)

# "Action" URLs (must use method POST)
urlpatterns += patterns('celerymanagementapp',    
    # General url pattern: worker/NAME/...
    (r'^worker/(?P<name>[-\w\d_.]+)/shutdown/$', 'views.kill_worker'),
    (r'^worker/(?P<name>[-\w\d_.]+)/subprocess/grow/$', 'views.grow_worker_pool'),
    (r'^worker/(?P<name>[-\w\d_.]+)/subprocess/shrink/$', 'views.shrink_worker_pool'),
)


urlpatterns += patterns('celerymanagementapp',
    url(r'^view/system/$', 'views.system_overview', name="system_overview_url"),
    url(r'^view/system/test/$', 'views.system_overview', name="system_overview_url", kwargs={ "test" : "true" }),
)

urlpatterns += patterns('celerymanagementapp',
    (r'^get/throughputs/$', 'views.get_throughput_data'),
    (r'^get/throughputs/(?P<taskname>[-\w\d_.]+)/$', 'views.get_throughput_data'),
    
    (r'^get/runtimes/$', 'views.get_runtime_data'),
    (r'^get/runtimes/(?P<taskname>[-\w\d_.]+)/$', 'views.get_runtime_data'),
    #(r'^get/workers/$', 'views.get_worker_data'),
    #(r'^get/tasks/$', 'views.get_defined_tasks'),
    (r'^get/dispatched_tasks/$', 'views.get_dispatched_tasks'),
    (r'^get/dispatched_tasks/(?P<taskname>[-\w\d_.]+)/$', 'views.get_dispatched_tasks'),   
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            { 'document_root' : settings.BASE_DIR + '/celerymanagementapp/media/' }),
    )
