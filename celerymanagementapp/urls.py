import datetime
from django.conf.urls.defaults import *

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
    (r'^get/throughputs/(?P<taskname>[-\w\d_.]+)/$', 'views.get_throughput_data'),
    (r'^get/runtimes/(?P<taskname>[-\w\d_.]+)/(?P<bin_count>[-\w\d_.]+)/(?P<bin_size>[-\w\d_.]+)/$', 'views.get_runtime_data'),
    (r'^visualize/throughputs/(?P<taskname>[-\w\d_.]+)/$', 'views.visualize_throughput'),
    (r'^visualize/runtimes/(?P<taskname>[-\w\d_.]+)/(?P<bin_count>[-\w\d_.]+)/(?P<bin_size>[-\w\d_.]+)/$', 'views.visualize_runtimes'),
    (r'^test/$', 'views.test_view'),
    #(r'^test/(?P<taskname>[-\w\d_.]+)/$', 'views.test_view'),
    )

