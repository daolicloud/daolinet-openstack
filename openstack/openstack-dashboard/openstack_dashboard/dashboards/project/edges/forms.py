import logging

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import forms
from horizon import messages
from horizon import exceptions
from horizon.utils import validators

from openstack_dashboard import api

LOG = logging.getLogger(__name__)


def limit_port_range(port):
    if port not in range(10000, 65000):
        raise ValidationError(_("Enter an integer value "
                                "between 10000 and 65000"))

class FirewallForm(forms.SelfHandlingForm):
    #required_css_class = 'required form-float'
    required_css_class = 'form-horizontal'

    gateway_ip = forms.ChoiceField(label=_("Select Gateway"),
            widget=forms.SelectWidget(attrs={'style': 'width: 500px'}))
    gateway_port = forms.IntegerField(label=_("Gateway Port (10000-65000"),
            validators=[limit_port_range],
            widget=forms.TextInput(attrs={'style': 'width: 510px'}))
    service_port = forms.IntegerField(label=_("Service Port"), min_value=1,
            validators=[validators.validate_port_range],
            widget=forms.TextInput(attrs={'style': 'width: 510px'}))

    def __init__(self, request, *args, **kwargs):
        super(FirewallForm, self).__init__(request, *args, **kwargs)
        choices = []
        tmp_choices = []

        instance = kwargs['initial']['instance']
        gateways = kwargs['initial']['gateways']
        for gateway in gateways:
            item = (gateway.hostname, gateway.vext_ip)
            if gateway.int_dev != gateway.ext_dev or \
                    gateway.vext_ip != gateway.ext_ip:
                choices.append(item)
            else:
                if gateway.hostname == host:
                    tmp_choices.append(item)

        if not choices:
            choices = tmp_choices

        if choices:
            choices.insert(0, ("", _("Select Gateway")))
        else:
            choices.insert(0, ("", _("No Gateway available")))
        self.fields['gateway_ip'].choices = choices

    def clean(self):
        data = super(forms.Form, self).clean()
        hostname = data.get("gateway_ip")
        gateway_port = data.get("gateway_port")
        service_port = data.get("service_port")
        if hostname and gateway_port and service_port:
            instance = self.initial['instance']
            try:
                api.daolicloud.firewall_exist(self.request,
                                              instance.id,
                                              hostname=hostname,
                                              gateway_port=gateway_port)
            except Exception as e:
                #msg = _("This gateway port already be used.")
                #raise forms.ValidationError(msg)
                raise forms.ValidationError(e.message)

        return data

    def handle(self, request, data):
        hostname = data['gateway_ip']
        gport = data['gateway_port']
        sport = data['service_port']
        instance = self.initial['instance']
        try:
            firewall = api.daolicloud.firewall_create(
                    request, instance.id, hostname, gport, sport)
            message = _('Create gateway %(gport)s, service %(sport)s to '
                         ' instance %(inst)s.') % {"gport": gport,
                                                   "sport": sport,
                                                   "inst": instance.name}
            messages.success(request, message)
            return firewall
        except Exception:
            redirect = reverse("horizon:project:edges:index")
            exceptions.handle(request,
                              _('Unable to add firewall.'),
                              redirect=redirect)
