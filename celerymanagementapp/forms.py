from django.forms import ModelForm

from celerymanagementapp.models import OutOfBandWorkerNode

class OutOfBandWorkerNodeForm(ModelForm):
    class Meta:
        model = OutOfBandWorkerNode
