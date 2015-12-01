import collections
import logging
import six.moves.urllib.parse as urlparse

import django
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import secret_key
from horizon.utils import validators

from openstack_dashboard import api
from openstack_dashboard.auth import User
from openstack_dashboard.exceptions import NOT_FOUND

LOG = logging.getLogger(__name__)

class BaseForm(forms.SelfHandlingForm):
    email = forms.EmailField(label=_("Email"))
    password = forms.RegexField(
        label=_("Password"),
        widget=forms.PasswordInput(render_value=False),
        regex=validators.password_validator(),
        error_messages={'invalid': validators.password_validator_msg()})
    confirm_password = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(render_value=False))

    def __init__(self, request, *args, **kwargs):
        request.user = User()
        super(BaseForm, self).__init__(request, *args, **kwargs)

    def clean(self):
        '''Check to make sure password fields match.'''
        data = super(BaseForm, self).clean()
        if 'password' in data:
            if data['password'] != data.get('confirm_password', None):
                raise ValidationError(_('Passwords do not match.'))
        return data

class CreateUserForm(BaseForm):
    name = forms.CharField(max_length=255, label=_("User Name"))
    no_autocomplete = True

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        ordering = ["name", "email", "password", "confirm_password"]

        if django.VERSION >= (1, 7):
            self.fields = collections.OrderedDict(
                (key, self.fields[key]) for key in ordering)
        else:
            self.fields.KeyOrder = ordering

    @sensitive_variables('data')
    def handle(self, request, data):
        domain = api.daolicloud.get_default_domain(self.request)
        try:
            desc = '%s tenant' % data['name']
            LOG.info('Creating user with name "%s"' % data['name'])
            new_tenant = api.daolicloud.tenant_create(request,
                                                    name=data['name'],
                                                    description=desc,
                                                    enabled=True,
                                                    domain=domain.id)
            new_user = api.daolicloud.user_create(request,
                                                name=data['name'],
                                                email=data['email'],
                                                password=data['password'],
                                                project=new_tenant.id,
                                                enabled=True,
                                                domain=domain.id)
            messages.success(request,
                             _('User "%s" was successfully created.')
                             % data['name'])
            return new_user
        except exceptions.Conflict:
            msg = _('User name "%s" is already used.') % data['name']
            exceptions.handle(request, msg, redirect=reverse('message'))
        except Exception:
            exceptions.handle(request,
                              _('Unable to create user.'),
                              redirect=reverse('message'))

class GetPasswordForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255, label=_("User Name"))
    email = forms.EmailField(label=_("Email")) 

    def __init__(self, request, *args, **kwargs):
        request.user = User()
        super(GetPasswordForm, self).__init__(request, *args, **kwargs)

    def clean(self):
        cleaned_data = super(GetPasswordForm, self).clean()
        username = cleaned_data.get("name")
        email = cleaned_data.get("email")
        if username and email:
            try:
                user = api.daolicloud.user_get_by_name(self.request, username)
            except NOT_FOUND as e:
                raise ValidationError(e.message)

            if user.email != email:
                msg = _('Username or email does not match.')
                raise ValidationError(msg)

            cleaned_data["user_id"] = user.id
        return cleaned_data

    def handle(self, request, data):
        params = {"email": data['email'],
                  "tid": secret_key.generate_key(),
                  "uid": data["user_id"]}

        url = urlparse.urlunsplit((request.META['wsgi.url_scheme'],
                                   request.get_host(),
                                   reverse('resetpassword'),
                                   urlparse.urlencode(params), None))

        request.session[params['tid']] = params
        request.session['active_url'] = url
        LOG.debug("Link: %s", url)
        messages.success(request, _("Please check your email and change "
                                    "your account password in 10 minitus!"))
        return True

class ResetPasswordForm(BaseForm):
    uid = forms.CharField(widget=forms.HiddenInput())
    #email = forms.CharField(widget=forms.HiddenInput())
    tid = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, request, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(request, *args, **kwargs)
        self.subject = "[Daolicloud] Change password successful."
        self.body = "Your new password: %s"
        for attr in ('uid', 'email', 'tid'):
            self.fields[attr].initial = request.REQUEST.get(attr)
        self.fields['email'].widget = forms.TextInput(
                                       attrs={'readonly': 'readonly'})

    @sensitive_variables('data', 'password')
    def handle(self, request, data):
        try:
            response = api.keystone.user_update_password(
                request, data['uid'], data['password'])
            messages.success(request, _(
                'Your password has been updated successfully, '
                'Please login again.'))
            #body = self.body % data['password']
            #send_email(data['email'], self.subject, body)
        except Exception:
            exceptions.handle(request, _("Unable to update password."),
                              redirect=reverse('horizon:message'))
        return True
