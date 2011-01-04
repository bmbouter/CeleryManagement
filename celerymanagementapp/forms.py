from django.forms import ModelForm

from celerymanagementapp.models import OutOfBandWorkerNode, Provider

class OutOfBandWorkerNodeForm(ModelForm):
    class Meta:
        model = OutOfBandWorkerNode

class ProviderForm(ModelForm):
    class Meta:
        model = Provider
