from django.core.urlresolvers import reverse
from django import template
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import forms
from horizon import tables
from horizon.utils import filters

from openstack_dashboard import api

class CreateGroupAction(tables.LinkAction):
    name = "create"
    verbose_name = _("Create VPCs")
    url = "horizon:project:vpcs:create"
    classes = ("ajax-modal",)
    icon = "plus"

    def allowed(self, request, project):
        return True

class UpdateMembersLink(tables.LinkAction):
    name = "members"
    verbose_name = _("Manage Members")
    url = "horizon:project:vpcs:update"
    classes = ("ajax-modal",)
    icon = "pencil"

    def get_link_url(self, group):
        step = 'update_members'
        base_url = reverse(self.url, args=[group.id])
        param = urlencode({"step": step})
        return "?".join([base_url, param])

class DeleteGroupAction(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete VPC",
            u"Delete VPCs",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted VPC",
            u"Deleted VPCs",
            count
        )

    def delete(self, request, obj_id):
        api.daolicloud.group_delete(request, obj_id)

def get_members(group):
    template_name = 'project/vpcs/_member_list.html'
    context = {"members": group.members}
    return template.loader.render_to_string(template_name, context)

class GroupTable(tables.DataTable):
    name = tables.Column('name', verbose_name=_('Name'))
    description = tables.Column(lambda obj: getattr(obj, 'description', None),
                                verbose_name=_('Description'),
                                form_field=forms.CharField(
                                    widget=forms.Textarea(attrs={'rows': 4}),
                                    required=False))
    members = tables.Column(get_members,
                            verbose_name=_("VPC Members"))
    created = tables.Column('created_at',
                            verbose_name=_('Time since created'),
                            filters=(filters.parse_isotime,
                                     filters.timesince_sortable),
                            attrs={'data-type': 'timesince'})


    class Meta(object):
        name = "vpcs"
        verbose_name = _("VPCs")                                  
        table_actions = (CreateGroupAction,)
        row_actions = (UpdateMembersLink, DeleteGroupAction) 
