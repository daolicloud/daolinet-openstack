import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import workflows

from openstack_dashboard import api

GROUP_MEMBER_SLUG = "update_members"
COMMON_HORIZONTAL_TEMPLATE = "project/vpcs/_common_horizontal_form.html"

LOG = logging.getLogger(__name__)

class CreateGroupInfoAction(workflows.Action):
    name = forms.CharField(label=_("Name"), max_length=64)
    description = forms.CharField(widget=forms.widgets.Textarea(
                                  attrs={'rows': 4}),
                                  label=_("Description"),
                                  required=False)

    class Meta(object):
        name = _("VPC Information")
        help_text = _("Create a vpc description")

class UpdateGroupInfoAction(CreateGroupInfoAction):
    class Meta(object):
        name = _("VPC Information")
        slug = 'update_info'
        help_text = _("Edit the vpc details.")

class CreateGroupInfo(workflows.Step):
    action_class = CreateGroupInfoAction
    template_name = COMMON_HORIZONTAL_TEMPLATE
    contributes = ("name", "description")

class UpdateGroupInfo(workflows.Step):
    action_class = UpdateGroupInfoAction
    template_name = COMMON_HORIZONTAL_TEMPLATE
    depends_on = ("group_id",)
    contributes = ("name", "description")


class UpdateMembersAction(workflows.MembershipAction):
    def __init__(self, request, *args, **kwargs):
        super(UpdateMembersAction, self).__init__(request, *args, **kwargs)
        err_msg = _('Unable to retrieve instance list. Please try again later.')
        group_id = None
        if 'group_id' in self.initial:
            group_id = self.initial['group_id']

        default_role_name = self.get_default_role_field_name()
        self.fields[default_role_name] = forms.CharField(required=False)
        self.fields[default_role_name].initial = 'member'

        # Get list of available members
        instances = []
        try:
            instances, _more = api.nova.server_list(self.request)
        except Exception:
            exceptions.handle(request, err_msg)

        all_groups = [(inst.id, inst.name) for inst in instances]

        field_name = self.get_member_field_name('member')
        self.fields[field_name] =  forms.MultipleChoiceField(required=False)
        self.fields[field_name].choices = all_groups
        self.fields[field_name].initial = []

        if group_id:
            try:
                members = api.daolicloud.group_member_get(request, group_id)
            except Exception:
                members = []
                exceptions.handle(request,
                                  err_msg,
                                  redirect=reverse("horizon:project:vpcs:index"))

            for member in members:
                self.fields[field_name].initial.append(member.instance_id)

    class Meta(object):
        name = _("VPC Members")
        slug = GROUP_MEMBER_SLUG

class UpdateGroupMembers(workflows.UpdateMembersStep):
    action_class = UpdateMembersAction
    available_list_title = _("All Instances")
    members_list_title = _("VPC Members")
    no_available_text = _("No instances found.")
    no_members_text = _("No members.")
    show_roles = False

    def contribute(self, data, context):
        if data:
            post = self.workflow.request.POST
            field = self.get_member_field_name('member')
            context[field] = post.getlist(field)
        return context

class CreateVPC(workflows.Workflow):
    slug = "create_vpc"
    name = _("Create VPC")
    finalize_button_name = _("Create VPC")
    success_message = _('Created new vpc "%s".')
    failure_message = _('Unable to create vpc "%s".')
    success_url = "horizon:project:vpcs:index"
    default_steps = (CreateGroupInfo, UpdateGroupMembers)

    def format_status_message(self, message):
        if "%s" in message:
            return message % self.context.get('name', 'unknown vpc')
        else:
            return message

    def _create_group(self, request, data):
        # create the group
        try:
            desc = data['description']
            group = api.daolicloud.group_create(request,
                                                name=data['name'],
                                                description=desc)
            return group
        except Exception:
            exceptions.handle(request, ignore=True)
            return

    def _update_group_members(self, request, data, group_id):
        # update group members
        member_step = self.get_step(GROUP_MEMBER_SLUG)
        field_name = member_step.get_member_field_name("member")
        member_list = data[field_name]
        members_to_add = len(member_list)

        try:
            for member in member_list:
                api.daolicloud.group_member_update(request,
                                                   group_id,
                                                   instance_id=member,
                                                   action='create')
                members_to_add -= 1
        except Exception:
            exceptions.handle(request,
                              _('Failed to add %(members_to_add)s'
                                ' instance members.')
                              % {'members_to_add': members_to_add})

    def handle(self, request, data):
        group = self._create_group(request, data)
        if not group:
            return False
        self._update_group_members(request, data, group.id)
        return True

class UpdateVPC(workflows.Workflow):
    slug = "update_vpc"
    name = _("Edit VPC")
    finalize_button_name = _("Save")
    success_message = _('Modified vpc "%s".')
    failure_message = _('Unable to modify vpc "%s".')
    success_url = "horizon:project:vpcs:index"
    default_steps = (UpdateGroupInfo, UpdateGroupMembers)

    def format_status_message(self, message):
        if "%s" in message:
            return message % self.context.get('name', 'unknown vpc')
        else:
            return message

    def _update_group(self, request, data):
        # update group info
        try:
            return api.daolicloud.group_update(
                request,
                data['group_id'],
                name=data['name'],
                description=data['description'])
        except:
            exceptions.handle(request, ignore=True)
            return

    def _update_group_members(self, request, data, group_id):
        # update group members
        try:
            members = api.daolicloud.group_member_get(request, group_id)
        except Exception:
            members = []
            exceptions.handle(request,
                              _('Unable to retrieve vpc members.'),
                              ignore=True)

        current_members = [member.instance_id for member in members]

        member_step = self.get_step(GROUP_MEMBER_SLUG)
        field_name = member_step.get_member_field_name("member")

        add_members = []
        for instance_id in data[field_name]:
            if instance_id not in current_members:
                add_members.append(instance_id)

        remove_members = []
        for instance_id in current_members:
            if instance_id not in data[field_name]:
                remove_members.append(instance_id)

        # count the change members
        members_to_modify = len(add_members) + len(remove_members)

        try:
            for member in add_members:
                api.daolicloud.group_member_update(request,
                                                   group_id,
                                                   instance_id=member,
                                                   action='create')
                members_to_modify -= 1

            for member in remove_members:
                api.daolicloud.group_member_update(request,
                                                   group_id,
                                                   instance_id=member,
                                                   action='delete')
                members_to_modify -= 1

            return True
        except Exception:
            exceptions.handle(request,
                              _('Failed to modify %(members_to_modify)s'
                                ' instance members.')
                              % {'members_to_modify': members_to_modify})
            return False

    def handle(self, request, data):
        group = self._update_group(request, data)
        if not group:
            return False

        member = self._update_group_members(request, data, data['group_id'])
        if not member:
            return False

        return True
