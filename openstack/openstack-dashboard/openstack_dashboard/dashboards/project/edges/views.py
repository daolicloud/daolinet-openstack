import logging
from django.core.urlresolvers import reverse_lazy
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon.utils import memoized

from openstack_dashboard import api

from openstack_dashboard.dashboards.project.edges \
    import tables as project_tables
from openstack_dashboard.dashboards.project.edges \
    import forms as project_forms

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = project_tables.InstancesTable
    template_name = 'project/edges/index.html'
    page_title = _("Distributed Firewall")

    def has_more_data(self, table):
        return self._more

    def get_data(self):
        marker = self.request.GET.get(
            project_tables.InstancesTable._meta.pagination_param, None)
        search_opts = self.get_filters({'marker': marker, 'paginate': True})
        # Gather our instances
        try:
            instances, self._more = api.nova.server_list(
                self.request,
                search_opts=search_opts)
        except Exception:
            self._more = False
            instances = []
            exceptions.handle(self.request,
                              _('Unable to retrieve instances.'))

        # Gather our flavors and images and correlate our instances to them
        if instances:
            #try:
            #    flavors = api.nova.flavor_list(self.request)
            #except Exception:
            #    flavors = []
            #    exceptions.handle(self.request, ignore=True)

            #try:
            #    # Handle pagination.
            #    images, more, prev = api.glance.image_list_detailed(
            #        self.request)
            #except Exception:
            #    images = []
            #    exceptions.handle(self.request, ignore=True)

            try:
                gateways = api.daolicloud.gateway_list(self.request)
            except Exception:
                gateways = []
                exceptions.handle(self.request, ignore=True)

            #full_flavors = SortedDict([(str(flavor.id), flavor)
            #                           for flavor in flavors])
            #image_map = SortedDict([(str(image.id), image)
            #                           for image in images])
            gateway_map = SortedDict([(gateway.hostname, gateway.vext_ip)
                                      for gateway in gateways])

            # Loop through instances to get flavor info.
            for instance in instances:
                #if hasattr(instance, 'image'):
                #    # Instance from image returns dict
                #    if isinstance(instance.image, dict):
                #        if instance.image.get('id') in image_map:
                #            instance.image = image_map[instance.image['id']]

                #try:
                #    flavor_id = instance.flavor["id"]
                #    if flavor_id in full_flavors:
                #        instance.full_flavor = full_flavors[flavor_id]
                #    else:
                #        # If the flavor_id is not in full_flavors list,
                #        # get it via nova api.
                #        instance.full_flavor = api.nova.flavor_get(
                #            self.request, flavor_id)
                #except Exception:
                #    msg = ('Unable to retrieve flavor "%s" for instance "%s".'
                #           % (flavor_id, instance.id))
                #    LOG.info(msg)

                instance.firewall = api.daolicloud.firewall_get(
                    self.request, instance.id)

                for firewall in instance.firewall:
                    firewall.gateway_ip = gateway_map.get(firewall.hostname)

        return instances

    def get_filters(self, filters):
        filter_action = self.table._meta._filter_action
        if filter_action:
            filter_field = self.table.get_filter_field()
            if filter_action.is_api_filter(filter_field):
                filter_string = self.table.get_filter_string()
                if filter_field and filter_string:
                    filters[filter_field] = filter_string
        return filters

class UpdateView(tables.DataTableView, forms.ModalFormView):
    table_class = project_tables.FirewallTable
    form_class = project_forms.FirewallForm
    form_id = "update_firewall_form"
    modal_header = _("Manage Firewall Rules")
    modal_id = "update_firewall_modal"
    template_name = 'project/edges/update.html'
    submit_url = "horizon:project:edges:update"
    success_url = reverse_lazy("horizon:project:edges:index")
    page_title = _("Manage Firewall Map")

    def _object_get(self, request):
        if not hasattr(self, 'gateways'):
            self.gateways = api.daolicloud.gateway_list(request)
        return self.gateways

    def get_data(self):
        firewalls = api.daolicloud.firewall_get(self.request,
                                                self.kwargs['id'])
        gateways = SortedDict((gateway.hostname, gateway.vext_ip)
                              for gateway in self._object_get(self.request))

        for firewall in firewalls:
            firewall.gateway_ip = gateways.get(firewall.hostname,
                                               firewall.hostname)

        return firewalls

    def get_initial(self):
        instance = api.nova.server_get(self.request, self.kwargs['id'])
        gateways = self._object_get(self.request)
        return {'instance': instance, 'gateways': gateways}

    @memoized.memoized_method
    def get_form(self, **kwargs):
        form_class = kwargs.get('form_class', self.get_form_class())
        return super(UpdateView, self).get_form(form_class)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        if self.request.is_ajax():
            context['hide'] = True
        context['instance_id'] = self.kwargs['id']
        return context

    def get(self, request, *args, **kwargs):
        # Table action handling
        handled = self.construct_tables()
        if handled:
            return handled
        return self.render_to_response(self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.get(request, *args, **kwargs)
