from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse as urlreverse
from django.contrib.auth.decorators import login_required

from celerymanagementapp.forms import OutOfBandWorkerNodeForm

def get_dispatched_tasks_data(request, name=None):
    if request.method == 'POST':
        f = open(settings.BASE_DIR + '/celerymanagementapp/media/test_data/chart_data.json', "r")

        return HttpResponse(f)

def system_overview(request):
    return render_to_response('celerymanagementapp/system.html',
            { "load_test_data" : "true" },
            context_instance=RequestContext(request))

def dashboard(request):
    return render_to_response('celerymanagementapp/dashboard.html',
            { "load_test_data" : "true" },
            context_instance=RequestContext(request))

def configure(request):
    out_of_band_worker_node_form = OutOfBandWorkerNodeForm()
    return render_to_response('celerymanagementapp/configure.html',
            {'outofbandworkernode_form': out_of_band_worker_node_form,
            "load_test_data" : "true" },
            context_instance=RequestContext(request))

def task_view(request, taskname=None):
    return render_to_response('celerymanagementapp/task.html',
            { "load_test_data" : "true",
            "taskname" : taskname, },
            context_instance=RequestContext(request))

def worker_view(request, workername=None):
    return render_to_response('celerymanagementapp/worker.html',
            { "load_test_data" : "true",
            "workername" : workername, },
            context_instance=RequestContext(request))

def kill_worker(request, name=None):
    if request.method == 'POST':
        return HttpResponse(name)
    else:
        return HttpResponse("failed")



@login_required
def task_demo_test_dataview(request):
    """ Very simple view for testing the task_demo_dataview function.  This is 
        only for testing, not for production code. 
    """
    from django.template import Template
    from django.template import RequestContext
    
    name = 'celerymanagementapp.testutil.tasks.simple_test'
    rate = 2.0
    runfor = 10.0
    
    send = urlreverse('celerymanagementapp.dataviews.task_demo_dataview')
    
    html = """\
    <html>
    <head>
    <script type="text/javascript" src="{{{{ CELERYMANAGEMENTAPP_MEDIA_PREFIX }}}}js/jquery.js" ></script>
    <script>
    
    function json() {{
    var query = '{{"name": "{name}", "rate":{rate}, "runfor":{runfor} }}';
    
    $.post(
        '{send}',
        query,
        function(data) {{
            //alert("Data loaded: " + data);
            //alert(data.data);
            //alert(data.data[0]);
        }},
        'json'
    );
    }}
    
    </script>
    </head>
    <body>
    <table>
      <tr><td>
        <form action="{send}" method="POST">
        {{% csrf_token %}}
        <input type="button" value="Send" onclick="json();"/>
        </form>
      </td></tr>
    </table>
    </body>
    </html>
    """
    html = html.format(send=send, name=name, rate=rate, runfor=runfor)
    t = Template(html)
    c = RequestContext(request)
    return HttpResponse(t.render(c))


@login_required
def worker_commands_test_view(request, name=None):
    """ Simple interface to test worker control commands. For testing only. """
    from django.template import Template
    from celerymanagementapp.dataviews import get_worker_subprocesses
    import pprint
    
    workername = name or 'all'
    kill = urlreverse( 'celerymanagementapp.views.kill_worker', 
                    kwargs={'name':workername} )
    grow = urlreverse( 'celerymanagementapp.views.grow_worker_pool', 
                    kwargs={'name':workername} )
    shrink = urlreverse('celerymanagementapp.views.shrink_worker_pool', 
                     kwargs={'name':workername} )
    subprocs = '{0}'.format(pprint.pformat(get_worker_subprocesses(),indent=4))
    
    html = """\
    <html>
    <body>
    <table>
      <tr><td>
        <form action="{kill}" method="POST">
        {{% csrf_token %}}
        <input type="submit" value="Kill Worker"/>
        </form>
      </td></tr>
      <tr><td>
        <form action="{grow}" method="POST">
        {{% csrf_token %}}
        <input type="submit" value="Grow Subprocesses"/>
        </form>
      </td></tr>
      <tr><td>
        <form action="{shrink}" method="POST">
        {{% csrf_token %}}
        <input type="submit" value="Shrink Subprocesses"/>
        </form>
      </td></tr>
    </table>
    <pre>
    {data}
    </pre>
    </body>
    </html>
    """
    html = html.format(kill=kill, grow=grow, shrink=shrink, data=subprocs)
    t = Template(html)
    c = RequestContext(request)
    return HttpResponse(t.render(c))




