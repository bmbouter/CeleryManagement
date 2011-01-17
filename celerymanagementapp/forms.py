from django.forms import ModelForm

from celerymanagementapp.models import OutOfBandWorkerNode, Provider

class OutOfBandWorkerNodeForm(ModelForm):
    class Meta:
        model = OutOfBandWorkerNode

class ProviderForm(ModelForm):
    class Meta:
        model = Provider
        fields = ('provider_name', 'provider_user_id', 'provider_key',
                'celeryd_username', 'ssh_key', 'celeryd_start_cmd', 'celeryd_stop_cmd', 'celeryd_status_cmd')
