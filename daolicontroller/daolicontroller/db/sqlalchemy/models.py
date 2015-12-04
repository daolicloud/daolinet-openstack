"""
SQLAlchemy models for daolicontroller data.
"""

from oslo_config import cfg
from oslo_db.sqlalchemy import models
from oslo_utils import uuidutils
from sqlalchemy import (Column, Index, Integer, BigInteger, Enum, String,
                        schema)
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm
from sqlalchemy import ForeignKey, DateTime, Boolean, Text, Float

from daolicontroller.db.sqlalchemy import types

CONF = cfg.CONF
BASE = declarative_base()

def MediumText():
    return Text().with_variant(MEDIUMTEXT(), 'mysql')

class NovaBase(models.SoftDeleteMixin,
                models.TimestampMixin,
                models.ModelBase):
    metadata = None

    def __copy__(self):
        """Implement a safe copy.copy()."""
        session = orm.Session()

        copy = session.merge(self, load=False)
        session.expunge(copy)
        return copy

    def save(self, session=None):
        from daolicontroller.db.sqlalchemy import api

        if session is None:
            session = api.get_session()

        super(NovaBase, self).save(session=session)


class Instance(BASE, NovaBase):
    """Represents a guest VM."""
    __tablename__ = 'instances'
    __table_args__ = (
        Index('uuid', 'uuid', unique=True),
        Index('instances_project_id_deleted_idx',
              'project_id', 'deleted'),
        Index('instances_reservation_id_idx',
              'reservation_id'),
        Index('instances_terminated_at_launched_at_idx',
              'terminated_at', 'launched_at'),
        Index('instances_uuid_deleted_idx',
              'uuid', 'deleted'),
        Index('instances_task_state_updated_at_idx',
              'task_state', 'updated_at'),
        Index('instances_host_node_deleted_idx',
              'host', 'node', 'deleted'),
        Index('instances_host_deleted_cleaned_idx',
              'host', 'deleted', 'cleaned'),
        schema.UniqueConstraint('uuid', name='uniq_instances0uuid'),
    )
    injected_files = []

    id = Column(Integer, primary_key=True, autoincrement=True)

    @property
    def name(self):
        try:
            base_name = CONF.instance_name_template % self.id
        except TypeError:
            # Support templates like "uuid-%(uuid)s", etc.
            info = {}
            # NOTE(russellb): Don't use self.iteritems() here, as it will
            # result in infinite recursion on the name property.
            for column in iter(orm.object_mapper(self).columns):
                key = column.name
                # prevent recursion if someone specifies %(name)s
                # %(name)s will not be valid.
                if key == 'name':
                    continue
                info[key] = self[key]
            try:
                base_name = CONF.instance_name_template % info
            except KeyError:
                base_name = self.uuid
        return base_name

    @property
    def _extra_keys(self):
        return ['name']

    user_id = Column(String(255))
    project_id = Column(String(255))

    image_ref = Column(String(255))
    kernel_id = Column(String(255))
    ramdisk_id = Column(String(255))
    hostname = Column(String(255))

    launch_index = Column(Integer)
    key_name = Column(String(255))
    key_data = Column(MediumText())

    power_state = Column(Integer)
    vm_state = Column(String(255))
    task_state = Column(String(255))

    memory_mb = Column(Integer)
    vcpus = Column(Integer)
    root_gb = Column(Integer)
    ephemeral_gb = Column(Integer)
    ephemeral_key_uuid = Column(String(36))

    # This is not related to hostname, above.  It refers
    #  to the nova node.
    host = Column(String(255))  # , ForeignKey('hosts.id'))

    # To identify the "ComputeNode" which the instance resides in.
    # This equals to ComputeNode.hypervisor_hostname.
    node = Column(String(255))

    # *not* flavorid, this is the internal primary_key
    instance_type_id = Column(Integer)

    user_data = Column(MediumText())

    reservation_id = Column(String(255))

    scheduled_at = Column(DateTime)
    launched_at = Column(DateTime)
    terminated_at = Column(DateTime)

    availability_zone = Column(String(255))

    # User editable field for display in user-facing UIs
    display_name = Column(String(255))
    display_description = Column(String(255))

    # To remember on which host an instance booted.
    # An instance may have moved to another host by live migration.
    launched_on = Column(MediumText())

    # NOTE(jdillaman): locked deprecated in favor of locked_by,
    # to be removed in Icehouse
    locked = Column(Boolean)
    locked_by = Column(Enum('owner', 'admin'))

    os_type = Column(String(255))
    architecture = Column(String(255))
    vm_mode = Column(String(255))
    uuid = Column(String(36), nullable=False)

    root_device_name = Column(String(255))
    default_ephemeral_device = Column(String(255))
    default_swap_device = Column(String(255))
    config_drive = Column(String(255))

    # User editable field meant to represent what ip should be used
    # to connect to the instance
    access_ip_v4 = Column(types.IPAddress())
    access_ip_v6 = Column(types.IPAddress())

    auto_disk_config = Column(Boolean())
    progress = Column(Integer)

    # EC2 instance_initiated_shutdown_terminate
    # True: -> 'terminate'
    # False: -> 'stop'
    # Note(maoy): currently Nova will always stop instead of terminate
    # no matter what the flag says. So we set the default to False.
    shutdown_terminate = Column(Boolean(), default=False)

    # EC2 disable_api_termination
    disable_terminate = Column(Boolean(), default=False)

    # OpenStack compute cell name.  This will only be set at the top of
    # the cells tree and it'll be a full cell name such as 'api!hop1!hop2'
    cell_name = Column(String(255))
    internal_id = Column(Integer)

    # Records whether an instance has been deleted from disk
    cleaned = Column(Integer, default=0)


class InstanceInfoCache(BASE, NovaBase):
    """Represents a cache of information about an instance
    """
    __tablename__ = 'instance_info_caches'
    __table_args__ = (
        schema.UniqueConstraint(
            "instance_uuid",
            name="uniq_instance_info_caches0instance_uuid"),)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # text column used for storing a json object of network data for api
    network_info = Column(MediumText())

    instance_uuid = Column(String(36), ForeignKey('instances.uuid'),
                           nullable=False)
    instance = orm.relationship(Instance,
                            backref=orm.backref('info_cache', uselist=False),
                            foreign_keys=instance_uuid,
                            primaryjoin=instance_uuid == Instance.uuid)

class Network(BASE, NovaBase):
    """Represents a network."""
    __tablename__ = 'networks'
    __table_args__ = (
        schema.UniqueConstraint("vlan", "deleted",
                                name="uniq_networks0vlan0deleted"),
       Index('networks_bridge_deleted_idx', 'bridge', 'deleted'),
       Index('networks_host_idx', 'host'),
       Index('networks_project_id_deleted_idx', 'project_id', 'deleted'),
       Index('networks_uuid_project_id_deleted_idx', 'uuid',
             'project_id', 'deleted'),
       Index('networks_vlan_deleted_idx', 'vlan', 'deleted'),
       Index('networks_cidr_v6_idx', 'cidr_v6')
    )

    id = Column(Integer, primary_key=True, nullable=False)
    label = Column(String(255))

    injected = Column(Boolean, default=False)
    cidr = Column(types.CIDR())
    cidr_v6 = Column(types.CIDR())
    multi_host = Column(Boolean, default=False)

    gateway_v6 = Column(types.IPAddress())
    netmask_v6 = Column(types.IPAddress())
    netmask = Column(types.IPAddress())
    bridge = Column(String(255))
    bridge_interface = Column(String(255))
    gateway = Column(types.IPAddress())
    broadcast = Column(types.IPAddress())
    dns1 = Column(types.IPAddress())
    dns2 = Column(types.IPAddress())

    vlan = Column(Integer)
    vpn_public_address = Column(types.IPAddress())
    vpn_public_port = Column(Integer)
    vpn_private_address = Column(types.IPAddress())
    dhcp_start = Column(types.IPAddress())

    rxtx_base = Column(Integer)

    project_id = Column(String(255))
    priority = Column(Integer)
    host = Column(String(255))  # , ForeignKey('hosts.id'))
    uuid = Column(String(36))

    mtu = Column(Integer)
    dhcp_server = Column(types.IPAddress())
    enable_dhcp = Column(Boolean, default=True)
    share_address = Column(Boolean, default=False)


class VirtualInterface(BASE, NovaBase):
    """Represents a virtual interface on an instance."""
    __tablename__ = 'virtual_interfaces'
    __table_args__ = (
        schema.UniqueConstraint("address", "deleted",
                        name="uniq_virtual_interfaces0address0deleted"),
        Index('virtual_interfaces_network_id_idx', 'network_id'),
        Index('virtual_interfaces_instance_uuid_fkey', 'instance_uuid'),
    )
    id = Column(Integer, primary_key=True, nullable=False)
    address = Column(String(255))
    network_id = Column(Integer)
    instance_uuid = Column(String(36), ForeignKey('instances.uuid'))
    uuid = Column(String(36))

class FixedIp(BASE, NovaBase):
    """Represents a fixed ip for an instance."""
    __tablename__ = 'fixed_ips'
    __table_args__ = (
        Index('fixed_ips_virtual_interface_id_fkey', 'virtual_interface_id'),
        Index('network_id', 'network_id'),
        Index('address', 'address'),
        Index('fixed_ips_instance_uuid_fkey', 'instance_uuid'),
        Index('fixed_ips_host_idx', 'host'),
        Index('fixed_ips_network_id_host_deleted_idx', 'network_id', 'host',
              'deleted'),
        Index('fixed_ips_address_reserved_network_id_deleted_idx',
              'address', 'reserved', 'network_id', 'deleted'),
        Index('fixed_ips_deleted_allocated_idx', 'address', 'deleted',
              'allocated'),
        Index('fixed_ips_deleted_allocated_updated_at_idx', 'deleted',
              'allocated', 'updated_at')
    )
    id = Column(Integer, primary_key=True)
    address = Column(types.IPAddress())
    network_id = Column(Integer)
    virtual_interface_id = Column(Integer)
    instance_uuid = Column(String(36), ForeignKey('instances.uuid'))
    # associated means that a fixed_ip has its instance_id column set
    # allocated means that a fixed_ip has its virtual_interface_id column set
    # TODO(sshturm) add default in db
    allocated = Column(Boolean, default=False)
    # leased means dhcp bridge has leased the ip
    # TODO(sshturm) add default in db
    leased = Column(Boolean, default=False)
    # TODO(sshturm) add default in db
    reserved = Column(Boolean, default=False)
    host = Column(String(255))
    network = orm.relationship(Network,
                           backref=orm.backref('fixed_ips'),
                           foreign_keys=network_id,
                           primaryjoin='and_('
                                'FixedIp.network_id == Network.id,'
                                'FixedIp.deleted == 0,'
                                'Network.deleted == 0)')
    instance = orm.relationship(Instance,
                            foreign_keys=instance_uuid,
                            primaryjoin='and_('
                                'FixedIp.instance_uuid == Instance.uuid,'
                                'FixedIp.deleted == 0,'
                                'Instance.deleted == 0)')
    virtual_interface = orm.relationship(VirtualInterface,
                           backref=orm.backref('fixed_ips'),
                           foreign_keys=virtual_interface_id,
                           primaryjoin='and_('
                                'FixedIp.virtual_interface_id == '
                                'VirtualInterface.id,'
                                'FixedIp.deleted == 0,'
                                'VirtualInterface.deleted == 0)')



#######################
class IPAvailabilityRange(BASE, NovaBase):
    __tablename__ = 'ipavailabilityranges'

    allocation_pool_id = Column(String(36), ForeignKey('ipallocationpools.id',
                                                       ondelete="CASCADE"),
                                primary_key=True)
    first_ip = Column(String(64), nullable=False)
    last_ip = Column(String(64), nullable=False)

    def __repr__(self):
        return "%s - %s" % (self.first_ip, self.last_ip)

class IPAllocationPool(BASE, NovaBase):
    __tablename__ = 'ipallocationpools'

    id = Column(String(36), primary_key=True, nullable=False)
    subnet_id = Column(String(36), ForeignKey('subnets.id',
                                              ondelete="CASCADE"))
    first_ip = Column(String(64), nullable=False)
    last_ip = Column(String(64), nullable=False)
    available_ranges = orm.relationship(IPAvailabilityRange,
                                    backref='ipallocationpool',
                                    lazy="joined",
                                    cascade='delete')

    def __repr__(self):
        return "%s - %s" % (self.first_ip, self.last_ip)

class Subnet(BASE, NovaBase):
    """Represents a tenant subnet.

    When a subnet is created the first and last entries will be created. These
    are used for the IP allocation.
    """
    __tablename__ = "subnets"

    id = Column(String(36), primary_key=True, nullable=False)
    name = Column(String(255))
    cidr = Column(String(64), nullable=False)
    gateway_ip = Column(String(64))
    network_id = Column(String(36), nullable=False)
    user_id = Column(String(36), nullable=False)
    allocation_pools = orm.relationship(IPAllocationPool,
                                    backref='subnet',
                                    lazy="joined",
                                    cascade='delete')

class Group(BASE, NovaBase):
    """Represents a vpc group."""

    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    project_id = Column(String(36), nullable=False)

class GroupMember(BASE, models.ModelBase):
    """Represents a vpc member."""

    __tablename__ = 'group_members'
    __table_args__ = (
        Index('members_group_id_instance_id_idx', 'group_id', 'instance_id'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    instance_id = Column(String(36), nullable=False)
    group = orm.relationship(Group,
                             backref='members',
                             foreign_keys=group_id,
                             primaryjoin=group_id == Group.id)
class Firewall(BASE, NovaBase):
    """Represents a port map."""

    __tablename__ = 'firewalls'
    __table_args = (
        schema.UniqueConstraint('hostname', 'gateway_port',
            name='uniq_hostname0gateway_port'),
    )

    id = Column(String(36), primary_key=True, nullable=False)
    hostname = Column(String(100), nullable=False)
    gateway_port = Column(Integer, nullable=False)
    service_port = Column(Integer, nullable=False)
    instance_id = Column(String(36), nullable=False)
    fake_zone = Column(Boolean, nullable=False)

class Gateway(BASE, NovaBase):
    __tablename__ = 'gateways'

    __table_args__ = (
        schema.UniqueConstraint(
            "datapath_id",
            name='uniq_gateways0datapath_id'),
        schema.UniqueConstraint(
            "hostname",
            name='uniq_gateways0hostname'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    datapath_id = Column(String(255), nullable=False)
    hostname = Column(String(255), nullable=False)
    idc_id = Column(Integer, default=0)
    idc_mac = Column(String(64))
    vint_dev = Column(String(255), nullable=False)
    vint_mac = Column(String(64), nullable=False)
    vext_dev = Column(String(255), nullable=False)
    vext_ip = Column(String(64))
    ext_dev = Column(String(255), nullable=False)
    ext_mac = Column(String(64), nullable=False)
    ext_ip = Column(String(64), nullable=False)
    int_dev = Column(String(255), nullable=False)
    int_mac = Column(String(64), nullable=False)
    int_ip = Column(String(64))
    zone_id = Column(String(36), nullable=False)
    count = Column(Integer, nullable=False, default=0)
    is_gateway = Column(Boolean, default=False)
    disabled = Column(Boolean, default=False)

# Deprecated
class SinGroup(BASE, models.ModelBase):
    """Represents a security group for instance."""

    __tablename__ = 'singroups'
    __table_args__ = (
        schema.UniqueConstraint(
            "start", "end", "project_id",
            name='uniq_singroups0start0end0project_id'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    start = Column(String(36), nullable=False)
    end = Column(String(36), nullable=False)
    project_id = Column(String(36), nullable=False)
