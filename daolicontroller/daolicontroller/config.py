from oslo_config import cfg
from oslo_db import options
from oslo_log import log

from daolicontroller.i18n import _
from daolicontroller import paths

CONF = cfg.CONF

_DEFAULT_SQL_CONNECTION = 'sqlite:///' + paths.state_path_def('daoliproxy.sqlite')

_DEFAULT_LOG_LEVELS = ['amqp=WARN', 'amqplib=WARN', 'boto=WARN',
                       'qpid=WARN', 'sqlalchemy=WARN', 'suds=INFO',
                       'oslo_messaging=INFO', 'iso8601=WARN',
                       'requests.packages.urllib3.connectionpool=WARN',
                       'urllib3.connectionpool=WARN', 'websocket=WARN',
                       'keystonemiddleware=WARN', 'routes.middleware=WARN',
                       'stevedore=WARN', 'glanceclient=WARN']

_DEFAULT_LOGGING_CONTEXT_FORMAT = ('%(asctime)s.%(msecs)03d %(process)d '
                                   '%(levelname)s %(name)s [%(request_id)s '
                                   '%(user_identity)s] %(instance)s'
                                   '%(message)s')



def parse_args(argv, **kwargs):
    log.set_defaults(_DEFAULT_LOGGING_CONTEXT_FORMAT, _DEFAULT_LOG_LEVELS)
    log.register_options(CONF)
    options.set_defaults(CONF, connection=_DEFAULT_SQL_CONNECTION,
                        sqlite_db='daolicontroller.sqlite')
    CONF(argv[1:],
         project='daolicontroller',
         version='1.0',
         **kwargs)
