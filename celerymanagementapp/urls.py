import datetime
from django.conf.urls.defaults import *

DATEMIN = r'(?P<datemin>\d{4}-\d{2}-\d{2})'
DATEMAX = r'(?P<datemax>\d{4}-\d{2}-\d{2})'
# accepts:  date_date   or   date_   or   _date
DATERANGE1 = '(?:'+DATEMIN+'_'+DATEMAX+'?)'
DATERANGE2 = '(?:_'+DATEMAX+')'

USERNAME = r'(?P<username>[a-zA-Z0-9]+)'##JOBID = r'(?:_job_(?P<jobid>[0-9]+))'

urlpatterns = patterns('celerymanagementapp',
    (r'^view/all/$', 'views.view_all_tasks'),
    (r'^view/throughputs/$', 'views.view_throughputs'),
    (r'^view/throughputs/(?P<taskname>[-\w\d_.]+)/$', 'views.view_throughputs'),
    )

