from django.conf.urls import patterns
from django.conf.urls import url

from openstack_dashboard.auth import views

urlpatterns = patterns(
    'openstack_dashboard.auth.views',
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^getpassword/$', views.GetPasswordView.as_view(), name='getpassword'),
    url(r'^resetpassword/$', views.ResetPasswordView.as_view(), name='resetpassword'),
    url(r'^message/$', 'message', name='message'),
)

