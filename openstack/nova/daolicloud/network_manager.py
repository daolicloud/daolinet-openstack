from oslo_log import log as logging
from oslo_utils import netutils

from nova import exception
from nova.i18n import _, _LE
from nova import objects
from nova.network import model as network_model
from nova.network.manager import NetworkManager

LOG = logging.getLogger(__name__)

class SimpleManager(NetworkManager):

    def init_host(self):
        pass

    def _allocate_fixed_ips(self, context, instance_id, host, networks,
                            **kwargs):
        """Calls allocate_fixed_ip once for each network."""
        requested_networks = kwargs.get('requested_networks')
        addresses_by_network = {}
        if requested_networks is not None:
            for request in requested_networks:
                addresses_by_network[request.network_id] = request.address
        for network in networks:
            if network['uuid'] in addresses_by_network:
                address = addresses_by_network[network['uuid']]
            else:
                address = None
            self.allocate_fixed_ip(context, instance_id, network,
                                   address=address)

    def allocate_fixed_ip(self, context, instance_id, network, **kwargs):
        """Gets a fixed ip."""
        LOG.debug('Allocate fixed ip on network %s', network['uuid'],
                  instance_uuid=instance_id)
        if kwargs.get('vpn', None):
            address = network['vpn_private_address']
            reserved = True
        else:
            address = kwargs.get('address', None)
            reserved = False

        if not address:
            address = None
        else:
            address = str(address)

        fip = objects.FixedIP.fixed_ip_add(context, instance_id, network['uuid'], 
                                           network['id'], context.project_id,
                                           address=address, reserved=reserved)

        vif = objects.VirtualInterface.get_by_instance_and_network(
            context, instance_id, network['id'])
        if vif is None:
            LOG.debug('vif for network %(network)s and instance '
                      '%(instance_id)s is used up, '
                      'trying to create new vif',
                      {'network': network['id'],
                       'instance_id': instance_id})
            vif = self._add_virtual_interface(context,
                instance_id, network['id'])

        fip.allocated = True
        fip.virtual_interface_id = vif.id
        fip.save()

        instance = objects.Instance.get_by_uuid(context, instance_id)

        LOG.debug('Allocated fixed ip %s on network %s', address,
                  network['uuid'], instance=instance)
        return address

    def get_instance_nw_info(self, context, instance_id, rxtx_factor,
                             host, instance_uuid=None, **kwargs):
        nw_info = super(SimpleManager, self).get_instance_nw_info(
                context, instance_id, rxtx_factor, host,
                instance_uuid=instance_uuid, **kwargs)

        for vif in nw_info:
            #vif['id'] = instance_id # temporary!Deprecated
            vif['type'] = network_model.VIF_TYPE_OVS
            #vif['devname'] = 'tap%s' % instance_id[:11]

        return nw_info

    def deallocate_fixed_ip(self, context, address, host=None, teardown=True,
            instance=None):
        objects.FixedIP.fixed_ip_delete(context, address, instance.uuid)

    def validate_networks(self, context, networks):
        """check if the networks exists and host
        is set to each network.
        """
        LOG.debug('Validate networks')
        if networks is None or len(networks) == 0:
            return

        network_uuids = [uuid for (uuid, fixed_ip) in networks]

        self._get_networks_by_uuids(context, network_uuids)

        for network_uuid, address in networks:
            if address is not None:
                if not netutils.is_valid_ip(address):
                    raise exception.FixedIpInvalid(address=address)

    def migrate_instance_start(self, context, instance_uuid,
                               floating_addresses,
                               rxtx_factor=None, project_id=None,
                               source=None, dest=None):
        pass
