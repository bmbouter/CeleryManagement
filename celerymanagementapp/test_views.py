from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse as urlreverse
from django.contrib.auth.decorators import login_required
from django.utils import simplejson

import random

from celerymanagementapp.forms import OutOfBandWorkerNodeForm, ProviderForm, PolicyModelForm
from celerymanagementapp.models import OutOfBandWorkerNode, Provider, InBandWorkerNode, PolicyModel

def system_overview(request):
    return render_to_response('celerymanagementapp/system.html',
            { "load_test_data" : "true" },
            context_instance=RequestContext(request))

def dashboard(request):
    return render_to_response('celerymanagementapp/dashboard.html',
            { "load_test_data" : "true" },
            context_instance=RequestContext(request))

def policy(request):
    policies = []
    for i in range(0,10):
        policy = PolicyModel(name="TestPolicy" + str(i), enabled="false", source="")
        policyForm = PolicyModelForm(instance=policy)
        policies.append({ "policy" : policy, "policyForm" : policyForm })

    return render_to_response('celerymanagementapp/policy.html',
            { "load_test_data" : "true",
                "policies" : policies},
            context_instance=RequestContext(request))

def chart(request):
    return render_to_response('celerymanagementapp/chart.html',
            { "load_test_data" : "true" },
            context_instance=RequestContext(request))

def configure(request):
    context = { "load_test_data": "true" }
    if settings.CELERYMANAGEMENTAPP_INFRASTRUCTURE_USE_MODE == "static":
        out_of_band_worker_node_form = OutOfBandWorkerNodeForm()
        OutOfBandWorkers = []

        for i in range(0,10):
            worker = OutOfBandWorkerNode(ip="4.5.6." + str(i), celeryd_username="Test Username")
            workerForm = OutOfBandWorkerNodeForm(instance=worker)
            OutOfBandWorkers.append({ "worker" : worker, "workerForm" : workerForm })

        context["outofbandworkernode_form"] = out_of_band_worker_node_form
        context["outofbandworkernodes"] = OutOfBandWorkers
    elif settings.CELERYMANAGEMENTAPP_INFRASTRUCTURE_USE_MODE == "dynamic":
        provider = Provider(provider_user_id="test456YUser", celeryd_username="Test Username", 
                            provider_name=Provider.PROVIDER_CHOICES[3][1], image_id="6sd6aF8dadSSa3")
        #provider = None
        providers = {}
        if provider:
            provider_form = ProviderForm(instance=provider)
            providers["provider_form"] = provider_form
            providers["provider"] = provider
        else:
            provider_form = ProviderForm()
            providers["provider_form"] = provider_form

        inbandnode = InBandWorkerNode(instance_id="adsfatte22d")
        inbandnode1 = InBandWorkerNode(instance_id="nfgttadfd")
        inbandnode2 = InBandWorkerNode(instance_id="nk^3764646d")

        context["provider"] = providers
        context["instances"] = [inbandnode, inbandnode1, inbandnode2]

    return render_to_response('celerymanagementapp/configure.html',
            context,
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


'''
Ajax views.
'''
def create_outofbandworker(request):
    if request.method == "POST":
        out_of_band_worker_node_form = OutOfBandWorkerNodeForm(request.POST, request.FILES)
        if out_of_band_worker_node_form.is_valid():
            return HttpResponse("success")
        else:
            errors = []
            for field in out_of_band_worker_node_form:
                errors.append({ 'field' : field.html_name,
                                'error' : field.errors })
            failed = { 'failure' : errors }
            json = simplejson.dumps(failed)
            return HttpResponse(json)

def create_provider(request):
    if request.method == "POST":
        provider_form = ProviderForm(request.POST, request.FILES)
        if provider_form.is_valid():
            return HttpResponse("success")
        else:
            errors = []
            for field in provider_form:
                errors.append({ 'field' : field.html_name,
                                'error' : field.errors })
            failed = { 'failure' : errors }
            json = simplejson.dumps(failed)
            return HttpResponse(json)

def get_images(request):
    images = [{ 'name': "Ubuntu34-postgresql", "id": "9ad9adf88dsa"}, 
                {'name': "Fedora-14-postgresql-Django", "id": "36d6a6gGHT"}, 
                {'name': "Fedora-14-Django-Celery1.222", "id": "&t6ad7fayYYy"}]
    json = simplejson.dumps(images)
    return HttpResponse(json, mimetype="application/json")


def create_policy(request):
    if request.method == "POST":
        policy_form = PolicyModelForm(request.POST)
        if policy_form.is_valid():
            return HttpResponse("success")
        else:
            errors = []
            for field in policy_form:
                errors.append({ 'field' : field.html_name,
                                'error' : field.errors })
            failed = { 'failure' : errors }
            json = simplejson.dumps(failed)
            return HttpResponse(json)


def delete_worker(request, worker_pk):
    """Deletes a worker"""
    random.seed()
    choice = random.randint(0, 1000)
    if not (choice % 2):
        json = simplejson.dumps("success")
        return HttpResponse(json)
    else:
        failed = { 'failure' : 'Instance failed to delete'}
        json = simplejson.dumps(failed)
        return HttpResponse(json)


def get_dispatched_tasks_data(request, name=None):
    if request.method == 'POST':
        f = open(settings.BASE_DIR + '/celerymanagementapp/media/test_data/chart_data.json', "r")

        return HttpResponse(f)

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
    var query = '{{"name": "[NAME]", "rate":{rate}, "runfor":{runfor} }}';
    query = query.replace("[NAME]", document.testform.taskname.value)
    
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
    <form name="testform" action="{send}" method="POST">
      <table>
        {{% csrf_token %}}
        <tr><td>
        <input type="text" name="taskname" value="{name}" size="90" />
        </td></tr>
        <tr><td>
        <input type="button" value="Send" onclick="json();"/>
        </td></tr>
      </table>
    </form>
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

