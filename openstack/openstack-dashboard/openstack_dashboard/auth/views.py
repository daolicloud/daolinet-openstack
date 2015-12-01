import logging

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard.auth import forms as auth_forms

LOG = logging.getLogger(__name__)

class RegisterView(forms.ModalFormView):
    form_class = auth_forms.CreateUserForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('message')
    page_title = _("Register")

class GetPasswordView(forms.ModalFormView):
    form_class = auth_forms.GetPasswordForm
    template_name = 'auth/getpassword.html'
    success_url = reverse_lazy('message')
    page_title = _("Forget Password")

class ResetPasswordView(forms.ModalFormView):
    form_class = auth_forms.ResetPasswordForm
    template_name = 'auth/resetpassword.html'
    success_url = reverse_lazy('message')
    page_title = _("Reset Password")

    def get_context_data(self, **kwargs):
        context = super(ResetPasswordView, self).get_context_data(**kwargs)
        user_id = self.request.REQUEST.get('uid')
        email = self.request.REQUEST.get('email')
        key = self.request.REQUEST.get('tid')

        if any((not user_id, not email, not key)):
            raise exceptions.NotFound()

        params = self.request.session.get(key, None)
        LOG.error("Params from session: %s", str(params))

        if params is None or params['uid'] != user_id or \
                params['email'] != email:
            #messages.error(self.request, _("Request expired."))
            raise exceptions.NotFound(_("Request expired."))

        return context

def message(request):
    template_name = "message.html"
    if not request._messages._loaded_messages:
        redirect_to = reverse('login')
        return HttpResponseRedirect(redirect_to)

    context = {'active_url': request.session.get('active_url')}
    if context['active_url']:
        del request.session['active_url']

    return TemplateResponse(request, template_name, context=context)
