from django.conf.urls import patterns
from django.conf.urls import url

from openstack_dashboard.dashboards.project.vpcs import views


urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^create/$', views.CreateView.as_view(), name='create'),
    url(r'^(?P<group_id>[^/]+)/update/$', views.UpdateView.as_view(),
        name='update'),
)
