from django.conf.urls import patterns
from django.conf.urls import url

from openstack_dashboard.dashboards.project.vpcs.views \
    import IndexView

VIEW_MOD = 'openstack_dashboard.dashboards.project.vpcs.views'

urlpatterns = patterns(VIEW_MOD,
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^show/$', 'show', name='show'),
    url(r'^create/$', 'create', name='create'),
    url(r'^delete/$', 'delete', name='delete'),
    url(r'^get/(?P<instance_id>[^/]+)/$', 'get', name='get'),
)
