import logging

from django.core.urlresolvers import reverse
from django import template
from django.template.defaultfilters import title
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tables
from horizon.utils import filters

from openstack_dashboard import api

from openstack_dashboard.dashboards.project.instances \
    import tables as instance_tables

class EditFirewall(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit Firewall Rules")
    url = "horizon:project:edges:update"
    classes = ("ajax-modal", "btn-edit")
    icon = "pencil"

    def allowed(self, request, instance=None):
        return (instance.status in instance_tables.SNAPSHOT_READY_STATES and
                not instance_tables.is_deleting(instance) and
                request.user.tenant_id == instance.tenant_id)

    def get_link_url(self, instance):
        base_url = reverse(self.url, args=(instance.id,))
        return base_url

class DeleteFirewall(tables.BatchAction):
    name = "delete"
    classes = ("btn-danger", "btn-detach") 
    icon = "remove"
    help_text = _("Deleted firewall rules are not recoverable.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Rule",
            u"Delete Rules",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleting Rule",
            u"Deleting Rules",
            count
        )

    def action(self, request, obj_id):
        api.daolicloud.firewall_delete(request, obj_id)

    def get_success_url(self, request):
        return reverse('horizon:project:edges:index')

def get_power_state(instance):
    return instance_tables.POWER_STATES.get(
            getattr(instance, "OS-EXT_STS:power_state", 0), '')

def get_firewall(instance):
    template_name = 'project/edges/_firewall_list.html'
    context = {"firewall": instance.firewall}
    return template.loader.render_to_string(template_name, context)

class InstancesTable(tables.DataTable):
    name = tables.Column("name",
                         link="horizon:project:instances:detail",
                         verbose_name=_("Instance Name"))
    ip = tables.Column(instance_tables.get_ips,
                       verbose_name=_("IP Address"),
                       attrs={'data-type': "ip"})
    az = tables.Column("availability_zone",
                       verbose_name=_("Availability Zone"))
    firewall = tables.Column(get_firewall,
                             verbose_name=_("Ingress Rules"))
    state = tables.Column(get_power_state,
                          filters=(title, filters.replace_underscores),
                          verbose_name=_("Power State"),
                          display_choices=instance_tables.POWER_DISPLAY_CHOICES)
    created = tables.Column("created",
                            verbose_name=_("Time since created"),
                            filters=(filters.parse_isotime,
                                     filters.timesince_sortable),
                            attrs={'data-type': 'timesince'})

    class Meta(object):
        name = "instances"
        verbose_name = _("Instances")
        row_actions = (EditFirewall,)

class FirewallTable(tables.DataTable):
    gateway_ip = tables.Column("gateway_ip",
                                verbose_name=_("Gateway Address"))
    gateway_port = tables.Column("gateway_port",
                                 verbose_name=_("Gateway Port"))
    service_port = tables.Column("service_port",
                                 verbose_name=_("Service Port"))

    def get_object_id(self, obj):
        return obj.id

    def get_object_display(self, datum):
        return "Service Port (%s)" % datum.gateway_port

    class Meta:
        name = "firewalls"
        verbose_name = _("Firewalls")
        table_actions = (DeleteFirewall,)
        row_actions = (DeleteFirewall,)
