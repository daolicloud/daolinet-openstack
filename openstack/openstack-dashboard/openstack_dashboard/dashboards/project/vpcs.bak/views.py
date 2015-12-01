from django.utils.translation import ugettext_lazy as _
import six

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import workflows

from openstack_dashboard import api

from openstack_dashboard.dashboards.project.vpcs \
    import forms as project_forms
from openstack_dashboard.dashboards.project.vpcs \
    import tables as project_tables
from openstack_dashboard.dashboards.project.vpcs \
    import workflows as project_workflows

GROUP_INFO_FIELDS = ("name", "description")


class IndexView(tables.DataTableView):
    table_class = project_tables.GroupTable
    template_name = 'project/vpcs/index.html'
    page_title = _("VPCs")

    def get_data(self):
        try:
            groups = api.daolicloud.group_list(self.request)
        except:
            groups = []
            exceptions.handle(self.request,
                              _("Unable to retrieve vpc information."))
        try:
            instances, _more = api.nova.server_list(self.request)
        except Exception:
            instances = []
            exceptions.handle(self.request,
                              _('Unable to retrieve instances.'))

        instance_dict = {}
        for instance in instances:
            instance.ip_groups = self._ip_filters(instance)
            instance_dict[instance.id] = instance

        for group in groups:
            for member in group.members:
                member['instance'] = instance_dict.get(member['instance_id'], {})

        return groups

    def _ip_filters(self, instance):
        ip_groups = {}

        for ip_group, addresses in six.iteritems(instance.addresses):
            ip_groups[ip_group] = {}
            ip_groups[ip_group]["floating"] = []
            ip_groups[ip_group]["non_floating"] = []

            for address in addresses:
                if ('OS-EXT-IPS:type' in address and
                   address['OS-EXT-IPS:type'] == "floating"):
                    ip_groups[ip_group]["floating"].append(address)
                else:
                    ip_groups[ip_group]["non_floating"].append(address)

        return ip_groups

class CreateView(workflows.WorkflowView):
    workflow_class = project_workflows.CreateVPC

class UpdateView(workflows.WorkflowView):
    workflow_class = project_workflows.UpdateVPC

    def get_initial(self):
        initial = super(UpdateView, self).get_initial()
        group_id = self.kwargs['group_id']
        group_info = api.daolicloud.group_get(self.request, group_id)
        for field in GROUP_INFO_FIELDS:
            initial[field] = getattr(group_info, field, None)

        initial['group_id'] = group_id
        return initial
