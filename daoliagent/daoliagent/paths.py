import os

from oslo_config import cfg

path_opts = [
    cfg.StrOpt('pybasedir',
               default=os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                    '../')),
               help='Directory where the daoliproxy python module is installed'),
    cfg.StrOpt('state_path',
               default='$pybasedir',
               help="Top-level directory for maintaining nova's state"),
]

CONF = cfg.CONF
CONF.register_opts(path_opts)


def state_path_def(*args):
    """Return an uninterpolated path relative to $state_path."""
    return os.path.join('$state_path', *args)
