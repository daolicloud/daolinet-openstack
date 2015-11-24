from ryu.lib import hub
hub.patch()

import sys

from oslo_config import cfg
from oslo_log import log as logging

from ryu.base.app_manager import AppManager
from ryu import cfg as ryu_cfg

from daoliagent import config

CONF = cfg.CONF
DEFAULT_CONFIG = ["/etc/nova/nova.conf"]

def main():
    config.parse_args(sys.argv, default_config_files=DEFAULT_CONFIG)
    if ryu_cfg.CONF is not CONF:
        ryu_cfg.CONF(project='ryu', args=[])
    logging.setup(CONF, "daoliagent")
    AppManager.run_apps(['daoliagent.ofa_agent'])
