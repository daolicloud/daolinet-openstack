"""Defines interface for DB access."""

from oslo_config import cfg
from oslo_db import concurrency
from oslo_log import log as logging

db_opts = [
    cfg.StrOpt('instance_name_template',
               default='instance-%08x',
               help='Template string to be used to generate instance names'),
]

CONF = cfg.CONF
CONF.register_opts(db_opts)

_BACKEND_MAPPING = {'sqlalchemy': 'daolicontroller.db.sqlalchemy.api'}

IMPL = concurrency.TpoolDbapiWrapper(CONF, backend_mapping=_BACKEND_MAPPING)

LOG = logging.getLogger(__name__)

def server_get(id):
    return IMPL.server_get(id)

def server_get_by_mac(macaddr, ipaddr, group=True):
    return IMPL.server_get_by_mac(macaddr, ipaddr, group=group)

def gateway_get_all():
    return IMPL.gateway_get_all()

def gateway_get_by_name(hostname):
    return IMPL.gateway_get_by_filter(hostname=hostname)

def gateway_get_by_datapath(datapath_id):
    return IMPL.gateway_get_by_filter(datapath_id=datapath_id)

def gateway_get_by_idc(idc_id):
    return IMPL.gateway_get_by_idc(idc_id)

def firewall_get_by_packet(hostname, dst_port):
    return IMPL.firewall_get_by_packet(hostname, dst_port)
