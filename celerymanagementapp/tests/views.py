from django.core.urlresolvers import reverse as urlreverse

from celerymanagementapp.tests import base, testcase_settings
from celerymanagementapp.models import OutOfBandWorkerNode
from celerymanagementapp.forms import OutOfBandWorkerNodeForm, ProviderForm

from django.conf import settings

class Configure_TestCase(base.CeleryManagement_DBTestCaseBase):
    def setUp(self):
        super(Configure_TestCase, self).setUp()
        self.configure_url = '/celerymanagementapp/view/configure/'
        self.outofbandworker_url = '/celerymanagementapp/outofbandworker/'

    def test_get_configure_status(self):
        with self.scoped_login('test_user','password'):
            response = self.client.get(self.configure_url)
        self.assertEquals(response.status_code, 200)

    def test_get_configure_template(self):
        with self.scoped_login('test_user','password'):
            response = self.client.get(self.configure_url)
        self.assertTemplateUsed(response, "celerymanagementapp/configure.html")
        
    def test_get_configure_blank_form_passive(self):
        settings.CELERYMANAGEMENTAPP_INFRASTRUCTURE_USE_MODE = 'passive'
        with self.scoped_login('test_user','password'):
            response = self.client.get(self.configure_url)
        self.assertContains(response, 'passive')

    def test_get_configure_blank_form_static(self):
        settings.CELERYMANAGEMENTAPP_INFRASTRUCTURE_USE_MODE = 'static'
        with self.scoped_login('test_user','password'):
            response = self.client.get(self.configure_url)
        out_of_band_worker_node_form = OutOfBandWorkerNodeForm()
        for field in out_of_band_worker_node_form:
            self.assertContains(response, field.html_name)

    def test_get_configure_blank_form_dynamic(self):
        settings.CELERYMANAGEMENTAPP_INFRASTRUCTURE_USE_MODE = 'dynamic'
        with self.scoped_login('test_user','password'):
            response = self.client.get(self.configure_url)
        provider_form = ProviderForm()
        for field in provider_form:
            self.assertContains(response, field.html_name)

    def test_get_configure_workers(self):
        f = open(testcase_settings.OUTOFBANDWORKER_SSH_KEY_FILE) #path to ssh_key file for testing
        with self.scoped_login('test_user','password'):
            self.client.post(self.outofbandworker_url, {
                            'ip' : testcase_settings.OUTOFBANDWORKER_IP,
                            'celeryd_username' : testcase_settings.OUTOFBANDWORKER_USERNAME,
                            'ssh_key' : f,
                            'celeryd_start_cmd' : testcase_settings.OUTOFBANDWORKER_CELERYD_START ,
                            'celeryd_stop_cmd' : testcase_settings.OUTOFBANDWORKER_CELERYD_STOP,
                            'celeryd_status_cmd' : testcase_settings.OUTOFBANDWORKER_CELERYD_STATUS,
                            'active' : 'on',
                                })
        f.close()
        with self.scoped_login('test_user','password'):
            response = self.client.get(self.configure_url)
        self.assertEquals(response.status_code, 200)
        ##self.assertEquals("success", response.content)
        self.assertTrue(OutOfBandWorkerNode.objects.filter(ip=testcase_settings.OUTOFBANDWORKER_IP).count() > 0)
        out_of_band_worker = OutOfBandWorkerNode.objects.filter(ip=testcase_settings.OUTOFBANDWORKER_IP)[0]
        self.assertContains(response, out_of_band_worker )
