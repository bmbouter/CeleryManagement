import datetime

from django.forms import ModelForm
from django.core.exceptions import ValidationError

from celerymanagementapp.models import OutOfBandWorkerNode, Provider
from celerymanagementapp.models import PolicyModel

from celerymanagementapp.policy import check_source as check_policy_source
from celerymanagementapp.policy import exceptions as policy_exceptions

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
    
    def clean_source(self):
        # check that it compiles
        print 'Cleaning Policy source...'
        source = self.cleaned_data['source']
        try:
            check_policy_source(source)
        except policy_exceptions.Error as e:
            raise ValidationError(e.formatted_message)
        except Exception as e:
            raise ValidationError(e.msg)
        return source
        
    def clean_modified(self):
        # we update the modified field, so we don't care about the old value
        print 'Cleaning Policy modified...'
        return datetime.datetime.now()
