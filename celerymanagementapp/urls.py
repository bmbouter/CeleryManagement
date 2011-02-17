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
    (r'^xy_query/dispatched_tasks/fieldinfo/$', 'dataviews.task_xy_metadata'),
    (r'^xy_query/dispatched_tasks/test/$', 'test_views.task_xy_dataview_test'),
    
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
    # For the following URLs, if 'all' is given instead of a worker name, *all* 
    # workers will be affected.
    # General url pattern: worker/NAME/...
    (r'^worker/(?P<name>[-\w\d_.]+)/shutdown/$', 'views.kill_worker'),
    (r'^worker/(?P<name>[-\w\d_.]+)/subprocess/grow/$', 'views.grow_worker_pool'),
    (r'^worker/(?P<name>[-\w\d_.]+)/subprocess/shrink/$', 'views.shrink_worker_pool'),
    # The following allow an explicit number of worker subprocess to be added/removed
    (r'^worker/(?P<name>[-\w\d_.]+)/subprocess/grow/(?P<num>\d+)/$', 'views.grow_worker_pool'),
    (r'^worker/(?P<name>[-\w\d_.]+)/subprocess/shrink/(?P<num>\d+)/$', 'views.shrink_worker_pool'),
    # for manual testing...
    (r'^worker/(?P<name>[-\w\d_.]+)/test_commands/$', 'test_views.worker_commands_test_view'),
    
    # manipulating outofbandworker ...
    (r'^outofbandworker/$', 'dataviews.create_or_update_outofbandworker'),
    (r'^outofbandworker/(?P<worker_pk>[\d]+)/delete/$', 'dataviews.delete_outofbandworker'),
    (r'^outofbandworker/(?P<worker_pk>[\d]+)/update/$', 'dataviews.create_or_update_outofbandworker'),
    (r'^outofbandworker/(?P<worker_pk>[\d]+)/power_state/$', 'dataviews.worker_power_dataview'),

    # manipulating provider ...
    (r'^provider/$', 'dataviews.create_provider'),
    (r'^provider/images/$', 'dataviews.provider_images'),
    (r'^provider/delete_worker/(?P<worker_pk>[\d]+)/$', 'dataviews.delete_inbandworker'),
    (r'^provider/(?P<provider_pk>[\d]+)/delete/$', 'dataviews.delete_provider'),
    
    (r'^taskdemo/launch/$', 'dataviews.task_demo_dataview'),
    (r'^taskdemo/status/(?P<uuid>[A-Fa-f0-9]{32})/$', 'dataviews.task_demo_status_dataview'),
    # for manual testing...
    (r'^taskdemo/test/$', 'test_views.task_demo_test_dataview'),
    
    (r'^policy/create/$', 'dataviews.policy_create'),
    (r'^policy/modify/(?P<policy_id>\d+)/$', 'dataviews.policy_modify'),
    (r'^policy/delete/(?P<policy_id>\d+)/$', 'dataviews.policy_delete'),
    (r'^policy/get/(?P<id>\d+)/$', 'dataviews.policy_get'),
    (r'^policy/list/$', 'dataviews.policy_list'),
    (r'^policy/test_form/$', 'test_views.policy_form_test'),
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

urlpatterns += patterns('',
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'celerymanagementapp/login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/celerymanagementapp/login/'}),
)

urlpatterns += patterns('celerymanagementapp.views',
    url(r'^view/system/$', 'system_overview', name="system_overview_url"),
    url(r'^view/task/(?P<taskname>[-\w\d_.]+)/$', 'task_view', name="task_view_url"),
    url(r'^view/worker/(?P<workername>[-\w\d_.]+)/$', 'worker_view', name="worker_view_url"),
    url(r'^view/dashboard/$', 'dashboard', name="dashboard_url"),
    url(r'^view/configure/$', 'configure', name="configure_url"),
    url(r'^view/policy/$', 'policy', name="policy_url"),
    url(r'^view/chart/$', 'chart', name="chart_url"),
)


if settings.DEBUG:
    urlpatterns += patterns('celerymanagementapp.test_views',
        url(r'^test/view/system/$', 'system_overview', name="test_system_overview_url"),
        url(r'^test/view/dashboard/$', 'dashboard', name="test_dashboard_url"),
        url(r'^test/view/configure/$', 'configure', name="test_configure_url"),
        url(r'^test/view/policy/$', 'policy', name="test_policy_url"),
        url(r'^test/view/chart/$', 'chart', name="test_chart_url"),
        #url(r'^test/view/task/(?P<taskname>[-\w\d_.]+)/$', 'task_view', name="task_view_url"),
        #url(r'^test/view/worker/(?P<workername>[-\w\d_.]+)/$', 'worker_view', name="worker_view_url")
    )
    urlpatterns += patterns('celerymanagementapp.test_views',
        #url(r'^test/post/worker/(?P<name>[-\w\d_.]+)/shutdown/$', 'kill_worker', name="test_kill_worker_url"),  # not found in test_views
        url(r'^test/post/xy_query/dispatched_tasks/$', 'get_dispatched_tasks_data', name='test_get_dispatched_tasks_url'),
    )
    urlpatterns += patterns('celerymanagementapp.test_views',
        url(r'^test/post/worker/(?P<name>[-\w\d_.]+)/shutdown/$', 'kill_worker', name='test_kill_worker_url'),
        url(r'^test/post/outofbandworker/(?P<worker_pk>[\d]+)/power_state/$', 'worker_power', name='test_worker_power_url'),
        url(r'^test/post/outofbandworker/$', 'create_or_update_outofbandworker', name="test_create_outofbandworker_url"),
        url(r'^test/post/outofbandworker/(?P<worker_pk>[\d]+)/update/$', 'create_or_update_outofbandworker', name="test_update_outofbandworker_url"),
        url(r'^test/post/outofbandworker/(?P<worker_pk>[\d]+)/delete/$', 'delete_outofbandworker', name="test_delete_outofbandworker_url"),
    )
    urlpatterns += patterns('celerymanagementapp.test_views',
        url(r'^test/post/provider/$', 'create_provider', name="test_create_provider_url"),
        url(r'^test/post/provider/(?P<provider_pk>[\d]+)/delete/$', 'delete_provider', name="test_delete_provider_url"),
        url(r'^test/post/provider/images/$', 'get_images', name="test_get_images_url"),
        url(r'^test/post/provider/delete_worker/(?P<worker_pk>[\d]+)/$', 'delete_worker', name='test_delete_worker_url'),
    )
    urlpatterns += patterns('celerymanagementapp.test_views',
        url(r'^test/post/policy/create/$', 'policy_create', name="test_create_policy_url"),
        url(r'^test/post/policy/modify/(?P<policy_id>\d+)/$', 'policy_modify', name="test_modify_policy_url"),
        url(r'^test/post/policy/delete/(?P<policy_id>\d+)/$', 'policy_delete', name="test_delete_policy_url"),
    )

    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            { 'document_root' : settings.BASE_DIR + '/celerymanagementapp/media/' }),
    )
