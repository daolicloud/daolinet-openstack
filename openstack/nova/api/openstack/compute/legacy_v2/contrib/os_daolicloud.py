import webob
from webob import exc

from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova import exception
from nova.i18n import _
from nova import objects

from oslo_config import cfg
from oslo_log import log as logging
from novaclient.client import HTTPClient

CONF = cfg.CONF
CONF.register_opt(cfg.StrOpt('controller_api',
                             default='http://127.0.0.1:8081',
                             help='The openflow controller api.'))

LOG = logging.getLogger(__name__)
authorize = extensions.extension_authorizer('compute', 'daolicloud')

class GatewayController(object):

    def index(self, req):
        """Returns all the gateways."""
        ctxt = req.environ['nova.context']
        gateways = objects.GatewayList.get_all(ctxt)
        return {'gateways': gateways}

class GroupController(wsgi.Controller):
    """The VPCs API."""

    def index(self, req):
        ctxt = req.environ['nova.context']
        groups = objects.GroupList.get_by_project(ctxt, ctxt.project_id)
        return {'groups': groups}

    def show(self, req, id):
        ctxt = req.environ['nova.context']
        group = objects.Group.get(ctxt, id)
        return {'group': group}

    def create(self, req, body):
        if not self.is_valid_body(body, 'group'):
            raise exc.HTTPUnprocessableEntity()

        ctxt = req.environ['nova.context']
        group = body['group']
        group_obj = objects.Group.create(ctxt,
                                         group['name'],
                                         group['description'],
                                         group['project_id'])
        return {'group': group_obj}

    def delete(self, req, id):
        ctxt = req.environ['nova.context']
        objects.Group.delete(ctxt, id)

    def update(self, req, id, body):
        if not self.is_valid_body(body, 'group'):
            raise exc.HTTPUnprocessableEntity()

        ctxt = req.environ['nova.context']
        name = body['group']['name']
        description = body['group']['description']

        try:
            group = objects.Group.update(ctxt, id,
                                         name=name,
                                         description=description)
        except exception.InstanceGroupNotFound as e:
            raise exc.HTTPNotFound(explanation=e.message)

        return {'group': group}

# Deprecated
class SinGroupController(wsgi.Controller):
    """The VPCs gui API."""

    def index(self, req):
        ctxt = req.environ['nova.context']
        groups = objects.SinGroupList.get_by_project(ctxt, ctxt.project_id)
        return {'groups': groups}

    def update(self, req, id, body):
        """Update vpc items."""
        if not self.is_valid_body(body, 'group'):
            raise exc.HTTPUnprocessableEntity()

        ctxt = req.environ['nova.context']
        action = body['group']['action']
        start = body['group']['start']
        end = body['group']['end']

        if action == 'delete':
            try:
                client = HTTPClient(ctxt.user_name,
                                    ctxt.auth_token,
                                    bypass_url=CONF.controller_api,
                                    auth_token=ctxt.auth_token)
                client.put('/v1.0/group', body={'sid': start, 'did': end})
            except Exception as e:
                LOG.error(e.message)

        if hasattr(objects.SinGroup, action):
            project_id = id or ctxt.project_id
            getattr(objects.SinGroup, action)(ctxt, project_id, start, end)

        return webob.Response(status_int=202)

class GroupMemberController(wsgi.Controller):
    """The VPCs Member API."""

    def show(self, req, id):
        ctxt = req.environ['nova.context']
        members = objects.GroupMemberList.get(ctxt, id)
        return {'members': members}

    def update(self, req, id, body):
        if not self.is_valid_body(body, 'member'):
            raise exc.HTTPUnprocessableEntity()

        ctxt = req.environ['nova.context']

        action = body['member'].get('action')
        if not action:
            raise exc.HTTPBadRequest(explanation='Action is not empty')

        instance_id = body['member']['instance_id']

        if hasattr(objects.GroupMember, action):
            getattr(objects.GroupMember, action)(
                ctxt, group_id=id, instance_id=instance_id)

        return webob.Response(status_int=202)


class FirewallController(wsgi.Controller):

    def show(self, req, id):
        ctxt = req.environ['nova.context']
        firewalls = objects.FirewallList.get_by_instance(ctxt, id)
        return {'firewalls': firewalls}

    def create(self, req, body):
        if not self.is_valid_body(body, 'firewall'):
            raise exc.HTTPUnprocessableEntity()

        ctxt = req.environ['nova.context']
        params = body['firewall']

        if not params.has_key('fake_zone'):
            params['fake_zone'] = False

        firewall = objects.Firewall.create(ctxt, **params)

        return {'firewall': firewall}

    def delete(self, req, id):
        ctxt = req.environ['nova.context']
        objects.Firewall.delete(ctxt, id)
        return webob.Response(status_int=202)

    @wsgi.response(202)
    @wsgi.action('os-check')
    def _action_exists(self, req, id, body):
        kwargs = body['os-check']
        if 'hostname' in kwargs and 'gateway_port' in kwargs:
            hostname = kwargs['hostname']
            gateway_port = kwargs['gateway_port']
        else:
            msg = _("Missing argument 'hostname' or 'gateways_port'")
            raise exc.HTTPBadRequest(explanation=msg)

        ctxt = req.environ['nova.context']

        try: 
            objects.Firewall.get(ctxt,
                                 hostname=hostname,
                                 gateway_port=gateway_port)
            msg = _("This gateway port already be in used.")
            raise exc.HTTPConflict(explanation=msg)
        except exception.SecurityGroupNotFoundForRule:
            return webob.Response(status_int=202)

class Os_daolicloud(extensions.ExtensionDescriptor):
    """Daolicloud Extension."""

    name = "Daolicloud"
    alias = "os-daolicloud"
    namespace = "http://www.daolicloud.com"
    updated = "2015-10-21T00:00:00Z"

    def get_resources(self):
        member_actions = {'action': 'POST'}
        resources = []
        resource = extensions.ResourceExtension('os-gateways',
                                                GatewayController())
        resources.append(resource)
        resource = extensions.ResourceExtension('os-groups',
                                                GroupController())
        resources.append(resource)
        # Deprecated
        resource = extensions.ResourceExtension('os-singroups',
                                                SinGroupController())
        resources.append(resource)
        # end
        resource = extensions.ResourceExtension('os-group-members',
                                                GroupMemberController())
        resources.append(resource)
        resource = extensions.ResourceExtension('os-firewalls',
                                                FirewallController(),
                                                member_actions=member_actions)
        resources.append(resource)
        return resources
