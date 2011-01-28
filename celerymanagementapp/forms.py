from django.forms import ModelForm

from celerymanagementapp.models import OutOfBandWorkerNode, Provider, PolicyModel

class OutOfBandWorkerNodeForm(ModelForm):
    class Meta:
        model = OutOfBandWorkerNode

class ProviderForm(ModelForm):
    class Meta:
        model = Provider
        fields = ('provider_name', 'provider_user_id', 'provider_key', 'image_id',
                'celeryd_username', 'ssh_key', 'celeryd_start_cmd', 'celeryd_stop_cmd', 'celeryd_status_cmd')

class PolicyModelForm(ModelForm):
    class Meta:
        model = PolicyModel
        fields = ('name', 'enabled', 'source', 'modified', 'last_run_time')
