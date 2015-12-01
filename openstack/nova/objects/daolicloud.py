from nova import db
from nova import objects
from nova.objects import base as obj_base
from nova.objects import fields


@obj_base.NovaObjectRegistry.register
class Gateway(obj_base.NovaPersistentObject, obj_base.NovaObject,
              obj_base.NovaObjectDictCompat):
    VERSION = '1.0'

    fields = {
        'id': fields.IntegerField(),
        'datapath_id': fields.StringField(nullable=True),
        'hostname': fields.StringField(nullable=True),
        'idc_id': fields.IntegerField(nullable=True),
        'idc_mac': fields.StringField(nullable=True),
        'vint_dev': fields.StringField(nullable=True),
        'vint_mac': fields.StringField(nullable=True),
        'vext_dev': fields.StringField(nullable=True),
        'vext_ip': fields.IPV4AddressField(nullable=True),
        'ext_dev': fields.StringField(nullable=True),
        'ext_mac': fields.StringField(nullable=True),
        'ext_ip': fields.IPV4AddressField(nullable=True),
        'int_dev': fields.StringField(nullable=True),
        'int_mac': fields.StringField(nullable=True),
        'int_ip': fields.IPV4AddressField(nullable=True),
        'zone_id': fields.UUIDField(nullable=True),
        'count': fields.IntegerField(nullable=True),
        'is_gateway': fields.BooleanField(),
        'disabled': fields.BooleanField(),
    }

    @staticmethod
    def _from_db_object(context, gateway, db_gateway):
        for field in gateway.fields:
            gateway[field] = db_gateway[field]
        gateway._context = context
        gateway.obj_reset_changes()
        return gateway

@obj_base.NovaObjectRegistry.register
class GatewayList(obj_base.ObjectListBase, obj_base.NovaObject):
    VERSION = '1.0'

    fields = {
        'objects': fields.ListOfObjectsField('Gateway'),
    }

    @obj_base.remotable_classmethod
    def get_all(cls, context):
        gateways = db.gateway_get_all(context)
        return obj_base.obj_make_list(context, cls(), objects.Gateway,
                                      gateways)

@obj_base.NovaObjectRegistry.register
class Group(obj_base.NovaPersistentObject, obj_base.NovaObject,
            obj_base.NovaObjectDictCompat):
    VERSION = '1.0'

    fields = {
        'id': fields.IntegerField(),
        'name': fields.StringField(nullable=True),
        'description': fields.StringField(nullable=True),
        'project_id': fields.UUIDField(nullable=True),
        'members': fields.ListOfObjectsField('GroupMember', nullable=True),
    }

    @staticmethod
    def _from_db_object(context, group, db_group):
        group.members = []
        if hasattr(db_group, 'members'):
            for member in db_group['members']:
                member_obj = GroupMember(
                    id=member['id'], instance_id=member['instance_id'],
                    group_id=member['group_id'])
                member_obj.obj_reset_changes()
                group.members.append(member_obj)

        for field in group.fields:
            if 'members' != field:
                group[field] = db_group[field]

        group.obj_reset_changes()
        return group

    @obj_base.remotable_classmethod
    def get(cls, context, id):
        db_group = db.group_get(context, id)
        return cls._from_db_object(context, cls(context), db_group)

    @obj_base.remotable_classmethod
    def update(cls, context, id, name=None, description=None):
        db_group = db.group_update(context, id, name=name,
                                   description=description)
        return cls._from_db_object(context, cls(context), db_group)

    @obj_base.remotable_classmethod
    def create(cls, context, name, description, project_id):
        db_group = db.group_create(context, name, description, project_id)
        return cls._from_db_object(context, cls(context), db_group)

    @obj_base.remotable_classmethod
    def delete(cls, context, id):
        db.group_delete(context, id)

@obj_base.NovaObjectRegistry.register
class GroupList(obj_base.ObjectListBase, obj_base.NovaObject):
    VERSION = '1.0'

    fields = {
        'objects': fields.ListOfObjectsField('Group'),
    }

    @obj_base.remotable_classmethod
    def get_by_project(cls, context, project_id):
        groups = db.group_get_by_project(context, project_id)
        return obj_base.obj_make_list(context, cls(context), objects.Group,
                                      groups)

@obj_base.NovaObjectRegistry.register
class GroupMember(obj_base.NovaObject, obj_base.NovaObjectDictCompat):
    VERSION = '1.0'

    fields = {
        'id': fields.IntegerField(),
        'instance_id': fields.StringField(nullable=True),
        'group_id': fields.IntegerField(),
    }

    @staticmethod
    def _from_db_object(context, member, db_member):
        for field in member.fields:
            member[field] = db_member[field]
        member._context = context
        member.obj_reset_changes()
        return member

    @obj_base.remotable_classmethod
    def create(cls, context, group_id=None, instance_id=None):
        db_member = db.group_member_create(context,
                                           group_id=group_id,
                                           instance_id=instance_id)
        return cls._from_db_object(context, cls(context), db_member)

    @obj_base.remotable_classmethod
    def delete(cls, context, group_id=None, instance_id=None):
        db.group_member_delete(context,
                               group_id=group_id,
                               instance_id=instance_id)

@obj_base.NovaObjectRegistry.register
class GroupMemberList(obj_base.ObjectListBase, obj_base.NovaObject):
    VERSION = '1.0'

    fields = {
        'objects': fields.ListOfObjectsField('GroupMember'),
    }

    @obj_base.remotable_classmethod
    def get(cls, context, group_id):
        members = db.group_member_get(context, group_id)
        return obj_base.obj_make_list(context, cls(context), objects.GroupMember,
                                      members)

@obj_base.NovaObjectRegistry.register
class Firewall(obj_base.NovaPersistentObject, obj_base.NovaObject,
               obj_base.NovaObjectDictCompat):
    VERSION = '1.0'

    fields = {
        'id': fields.UUIDField(nullable=True),
        'hostname': fields.StringField(nullable=True),
        'gateway_port': fields.IntegerField(nullable=True),
        'service_port': fields.IntegerField(nullable=True),
        'instance_id': fields.UUIDField(nullable=True),
        'fake_zone': fields.BooleanField()
        }

    @staticmethod
    def _from_db_object(context, firewall, db_firewall):
        for field in firewall.fields:
            firewall[field] = db_firewall[field]
        firewall._context = context
        firewall.obj_reset_changes()
        return firewall

    @obj_base.remotable_classmethod
    def create(cls, context, **firewall):
        db_firewall = db.firewall_create(context, **firewall)
        return cls._from_db_object(context, cls(context), db_firewall)

    @obj_base.remotable_classmethod
    def delete(cls, context, id):
        db.firewall_delete(context, id)

    @obj_base.remotable_classmethod
    def get(cls, context, hostname=None, gateway_port=None):
        db_firewall = db.firewall_get(context,
                                      hostname=hostname,
                                      gateway_port=gateway_port)
        return cls._from_db_object(context, cls(context), db_firewall)

@obj_base.NovaObjectRegistry.register
class FirewallList(obj_base.ObjectListBase, obj_base.NovaObject):
    VERSION = '1.0'

    fields = {
        'objects': fields.ListOfObjectsField('Firewall'),
    }

    @obj_base.remotable_classmethod
    def get_by_instance(cls, context, id):
        firewalls = db.firewall_get_by_instance(context, id)
        return obj_base.obj_make_list(context, cls(), objects.Firewall,
                                      firewalls)

# Deprecated
@obj_base.NovaObjectRegistry.register
class SinGroup(obj_base.NovaObject, obj_base.NovaObjectDictCompat):
    VERSION = '1.0'

    fields = {
        'id': fields.IntegerField(),
        'start': fields.UUIDField(nullable=True),
        'end': fields.UUIDField(nullable=True),
        'project_id': fields.UUIDField(nullable=True)
    }

    @staticmethod
    def _from_db_object(context, group, db_group):
        for field in group.fields:
            group[field] = db_group[field]
        group._context = context
        group.obj_reset_changes()
        return group

    @obj_base.remotable_classmethod
    def create(cls, context, project_id, start, end):
        db_group = db.singroup_create(context, project_id, start, end)
        return cls._from_db_object(context, cls(context), db_group)

    @obj_base.remotable_classmethod
    def delete(cls, context, project_id, start, end):
        db_group = db.singroup_delete(context, project_id, start, end)

@obj_base.NovaObjectRegistry.register
class SinGroupList(obj_base.ObjectListBase, obj_base.NovaObject):
    VERSION = '1.0'

    fields = {
        'objects': fields.ListOfObjectsField('SinGroup'),
    }

    @obj_base.remotable_classmethod
    def get_by_project(cls, context, project_id):
        groups = db.singroup_get_by_project(context, project_id)
        return obj_base.obj_make_list(context, cls(context), objects.SinGroup,
                                      groups)
