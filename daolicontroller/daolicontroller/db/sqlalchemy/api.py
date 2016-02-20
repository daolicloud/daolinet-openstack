"""Implementation of SQLAlchemy backend."""

import sys
import threading

from oslo_config import cfg
from oslo_db import options as oslo_db_options
from oslo_db.sqlalchemy import session as db_session
from oslo_log import log as logging
from oslo_utils import uuidutils


from sqlalchemy import and_, or_
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload

from daolicontroller.db.sqlalchemy import models
from daolicontroller.i18n import _
from daolicontroller import exception
#from daolicontroller import model as network_model

CONF = cfg.CONF

LOG = logging.getLogger(__name__)

_ENGINE_FACADE = None
_LOCK = threading.Lock()

def _create_facade_lazily(conf_group):
    global _LOCK, _ENGINE_FACADE
    if _ENGINE_FACADE is None:
        with _LOCK:
            if _ENGINE_FACADE is None:
                _ENGINE_FACADE = db_session.EngineFacade.from_config(CONF)
    return _ENGINE_FACADE

def get_engine(use_slave=False):
    facade = _create_facade_lazily(CONF.database)
    return facade.get_engine(use_slave=use_slave)

def get_session(use_slave=False, **kwargs):
    facade = _create_facade_lazily(CONF.database)
    return facade.get_session(use_slave=use_slave, **kwargs)

def get_backend():
    """The backend is this module itself."""
    return sys.modules[__name__]

def model_query(*args, **kwargs):
    session = kwargs.get('session') or get_session()
    query = session.query(*args)
    return query

NIC_NAME_LEN = 14

def _instance_get_network(instance_uuid, session=None):
    session = session or get_session()

    if not uuidutils.is_uuid_like(instance_uuid):
        raise exception.InvalidUUID(uuid=instance_uuid)

    vif_and = and_(models.VirtualInterface.id ==
                   models.FixedIp.virtual_interface_id,
                   models.VirtualInterface.deleted == 0)
    result = model_query(models.FixedIp, models.Instance.uuid,
                         models.Instance.host, models.Instance.project_id,
                         session=session).\
                filter_by(instance_uuid=instance_uuid).\
                outerjoin(models.VirtualInterface, vif_and).\
                join(models.Instance,
                models.Instance.uuid==models.FixedIp.instance_uuid).\
                options(contains_eager("virtual_interface")).\
                first()

    if not result or not result.FixedIp.virtual_interface:
        raise exception.FixedIpNotFoundForInstance(instance_uuid=instance_uuid)

    result.address = result.FixedIp.address
    result.mac_address = result.FixedIp.virtual_interface.address
    devname = "tap" + result.FixedIp.virtual_interface.uuid
    result.devname = devname[:NIC_NAME_LEN]

    return result

def server_get(id):
    """Get a single instance with the given instance_id."""
    #session = get_session()
    #result = model_query(models.Instance, session=session).\
    #        filter_by(uuid=id).\
    #        first()


    #if not result:
    #    raise exception.InstanceNotFound(instance_id=id)

    #result.info = network_model.NetworkInfo.hydrate(result.info_cache)
    #result = _instance_get_network(id, session=session)
    #return (result, network)
    return _instance_get_network(id)



def __server_get(id, gateway=False, session=None):
    session = session or get_session()
    tables = [models.Instance]
    if gateway:
        tables.append(models.Gateway)

    query = model_query(*tables, session=session)

    if gateway:
        query = query.join(models.Gateway, models.Gateway.hostname==models.Instance.host)

    result = query.filter(models.Instance.id==id).first()
    if result:
        instance_network = model_query(models.InstanceNetwork, session=session). \
                filter_by(instance_id=result.Instance.id).first()

        if not instance_network:
            return None

        result.Instance.address = instance_network['address']
        result.Instance.mac_address = instance_network['mac_address']

    return result


def server_get_by_mac(macaddr, ipaddr, group=True):
    session = get_session()
    data = {'has_more': False, 'src': None, 'dst': None}
    query = model_query(models.Instance, session=session).\
            filter(models.Instance.uuid==models.VirtualInterface.instance_uuid)

    src = query.filter(models.VirtualInterface.address==macaddr).first()

    if src is not None:
        data['src'] = _instance_get_network(src.uuid)
        dst = query.filter(models.FixedIp.address==ipaddr).\
                filter(models.FixedIp.virtual_interface_id==models.VirtualInterface.id).\
                filter(models.Instance.project_id==src.project_id).\
                first()

        if dst is not None:
            data['dst'] = _instance_get_network(dst.uuid)
            if group:
                query = model_query(models.SinGroup,
                                    session=session).filter(or_(
                        and_(models.SinGroup.start==src.uuid,
                             models.SinGroup.end==dst.uuid),
                        and_(models.SinGroup.start==dst.uuid,
                             models.SinGroup.end==src.uuid)))
                if query.first():
                    data['has_more'] = True
    return data


def __server_get_by_mac(macaddr, ipaddr, group=True):
    session = get_session()
    data = {'has_more': False, 'src': None, 'dst': None}
    query = model_query(models.Instance.id, models.Instance.host,
                        models.Instance.user_id, models.Instance.host,
                        models.InstanceNetwork.address,
                        models.InstanceNetwork.mac_address,
                        session=session).filter(
            models.Instance.id==models.InstanceNetwork.instance_id)

    src = query.filter(models.InstanceNetwork.mac_address==macaddr).first()

    if src is not None:
        data['src'] = src
        dst = query.filter(models.InstanceNetwork.address==ipaddr,
                           models.Instance.user_id==src.user_id).first()
        if dst is not None:
            data['dst'] = dst
            if group:
                query = model_query(models.SinGroup,
                                    session=session).filter(or_(
                        and_(models.SinGroup.start==src.id,
                             models.SinGroup.end==dst.id),
                        and_(models.SinGroup.start==dst.id,
                             models.SinGroup.end==src.id)))
                if query.first():
                    data['has_more'] = True
    return data

def gateway_get_by_filter(datapath_id=None, hostname=None):
    query = model_query(models.Gateway)

    if datapath_id is not None:
        query = query.filter_by(datapath_id=datapath_id)

    if hostname is not None:
        query = query.filter_by(hostname=hostname)

    return query.first()

def gateway_get_all():
    return model_query(models.Gateway).all()

def gateway_get_by_idc(idc_id):
    query = model_query(models.Gateway).filter_by(idc_id=idc_id)

    _query = query.filter(or_(
                models.Gateway.vext_ip!=models.Gateway.ext_ip,
                models.Gateway.int_dev!=models.Gateway.ext_dev))

    result = _query.filter_by(disabled=False).all()

    if not result:
        result = query.all()

    return result

def firewall_get_by_packet(hostname, dst_port):
    session = get_session()
    result = model_query(models.Firewall, session=session).\
        filter_by(hostname=hostname, gateway_port=dst_port).\
        first()

    if result:
        instance = _instance_get_network(result.instance_id, session=session)

        if instance:
            instance.service_port = result.service_port

        result = instance

    return result

def __firewall_get_by_packet(hostname, dst_port):
    session = get_session()
    query = model_query(models.Instance, models.Gateway,
                        models.Firewall.service_port, session=session).filter(
        models.Instance.id==models.Firewall.instance_id).filter(
            and_(models.Firewall.hostname==hostname,
                 models.Firewall.gateway_port==dst_port)).filter(
        models.Instance.host==models.Gateway.hostname)

    result = query.first()
    if result:
        instance_network = model_query(models.InstanceNetwork, session=session).\
                filter_by(instance_id=result.Instance.id).first()

        if not instance_network:
            return None

        result.Instance.address = instance_network['address']
        result.Instance.mac_address = instance_network['mac_address']

    return result
