import datetime
import calendar
import time

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from djcelery.models import WorkerState, TaskState


def view_all_tasks(self):
    self.TaskState = TaskState
    self.WorkerState = WorkerState

    return HttpResponse(self.TaskState.objects.all());

# Create your views here.
