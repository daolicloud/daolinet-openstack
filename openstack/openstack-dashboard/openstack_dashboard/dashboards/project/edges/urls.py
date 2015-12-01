from django.conf.urls import patterns
from django.conf.urls import url

from openstack_dashboard.dashboards.project.edges.views \
    import IndexView, UpdateView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^(?P<id>[^/]+)/$', UpdateView.as_view(), name='update'),
)
