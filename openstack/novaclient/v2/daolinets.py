"""
Daolicloud Network interface.
"""
from novaclient import base

class Network(base.Resource):

    def update(self):
        self.manager.update(self)

class NetworkManager(base.Manager):
    resource_class = Network

    def group_list(self):
        return self._list('/os-groups', 'groups')

    def group_get(self, id):
        return self._get('/os-groups/%s' % id, 'group')

    def group_create(self, name=None, description=None, project_id=None):
        body = {'group': {
                'name': name,
                'description': description,
                'project_id': project_id}}
        return self._create('/os-groups', body, 'group')

    def group_delete(self, id):
        self._delete('/os-groups/%s' % id)

    def group_update(self, group_id, **kwargs):
        body = {'group': kwargs}
        return self._update('/os-groups/%s' % group_id, body, 'group')

    def group_member_get(self, group_id):
        return self._list('/os-group-members/%s' % group_id, 'members')

    def group_member_update(self, group_id, instance_id=None, action=None):
        body = {'member': {'action': action, 'instance_id': instance_id}}
        self._update('/os-group-members/%s' % group_id, body)

    def gateway_list(self):
        return self._list('/os-gateways', 'gateways')

    def firewall_get_by_instance(self, instance):
        return self._list('/os-firewalls/%s' % base.getid(instance),
                          'firewalls')

    def firewall_exists(self, instance, **kwargs):
        self._action('os-check', instance, kwargs)

    def firewall_create(self, **kwargs):
        body = {'firewall': kwargs}
        return self._create('/os-firewalls', body, 'firewall')

    def firewall_delete(self, id):
        return self._delete('/os-firewalls/%s' % id)

    def _action(self, action, server, info=None, **kwargs):
        body = {action: info}
        url = '/os-firewalls/%s/action' % base.getid(server)
        return self.api.client.post(url, body=body)

    # Deprecated
    def singroup_list(self):
        return self._list('/os-singroups', 'groups')

    def singroup_update(self, project_id, **kwargs):
        body = {'group': kwargs}
        self._update('/os-singroups/%s' % project_id, body)
