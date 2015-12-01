import collections
import logging

from oslo_utils import netutils

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import six.moves.urllib.parse as urlparse

from keystoneclient import exceptions as keystone_exceptions

from openstack_auth import backend
from openstack_auth import utils as auth_utils

from horizon import exceptions
from horizon import messages
from horizon.utils import functions as utils
from horizon.utils.memoized import memoized  # noqa

from openstack_dashboard.api import base
from openstack_dashboard import policy


LOG = logging.getLogger(__name__)
DEFAULT_ROLE = None


# Set up our data structure for managing Identity API versions, and
# add a couple utility methods to it.
class IdentityAPIVersionManager(base.APIVersionManager):
    def upgrade_v2_user(self, user):
        if getattr(user, "project_id", None) is None:
            user.project_id = getattr(user, "default_project_id",
                                      getattr(user, "tenantId", None))
        return user

    def get_project_manager(self, *args, **kwargs):
        if VERSIONS.active < 3:
            manager = keystoneclient(*args, **kwargs).tenants
        else:
            manager = keystoneclient(*args, **kwargs).projects
        return manager


VERSIONS = IdentityAPIVersionManager(
    "identity", preferred_version=auth_utils.get_keystone_version())


# Import from oldest to newest so that "preferred" takes correct precedence.
try:
    from keystoneclient.v2_0 import client as keystone_client_v2
    VERSIONS.load_supported_version(2.0, {"client": keystone_client_v2})
except ImportError:
    pass

try:
    from keystoneclient.v3 import client as keystone_client_v3
    VERSIONS.load_supported_version(3, {"client": keystone_client_v3})
except ImportError:
    pass


def _get_endpoint_url(request, endpoint_type, catalog=None):
    if getattr(request.user, "service_catalog", None):
        url = base.url_for(request,
                           service_type='identity',
                           endpoint_type=endpoint_type)
    else:
        auth_url = getattr(settings, 'OPENSTACK_KEYSTONE_URL')
        url = request.session.get('region_endpoint', auth_url)

    # TODO(gabriel): When the Service Catalog no longer contains API versions
    # in the endpoints this can be removed.
    url = url.rstrip('/')
    url = urlparse.urljoin(url, 'v%s' % VERSIONS.active)

    return url

def keystoneclient(request, admin=False):
    user = request.user
    if admin:
        endpoint_type = 'adminURL'
    else:
        endpoint_type = getattr(settings,
                                'OPENSTACK_ENDPOINT_TYPE',
                                'internalURL')

    api_version = VERSIONS.get_active_version()

    # Take care of client connection caching/fetching a new client.
    # Admin vs. non-admin clients are cached separately for token matching.
    cache_attr = "_keystoneclient_admin" if admin \
        else backend.KEYSTONE_CLIENT_ATTR
    if (hasattr(request, cache_attr) and
        (not user.token.id or
         getattr(request, cache_attr).auth_token == user.token.id)):
        conn = getattr(request, cache_attr)
    else:
        endpoint = _get_endpoint_url(request, endpoint_type)
        magic_tuple = netutils.urlsplit(endpoint)
        scheme, netloc, path, query, frag = magic_tuple
        port = magic_tuple.port
        if port is None:
            port = 80
        new_netloc = netloc.replace(':%d' % port, ':%d' % (35357,))
        endpoint = urlparse.urlunsplit(
            (scheme, new_netloc, path, query, frag))
        insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
        cacert = getattr(settings, 'OPENSTACK_SSL_CACERT', None)
        LOG.debug("Creating a new keystoneclient connection to %s." % endpoint)
        remote_addr = request.environ.get('REMOTE_ADDR', '')
        conn = api_version['client'].Client(token=user.token.id,
                                            endpoint=endpoint,
                                            original_ip=remote_addr,
                                            insecure=insecure,
                                            cacert=cacert,
                                            auth_url=endpoint,
                                            debug=settings.DEBUG)
        setattr(request, cache_attr, conn)
    return conn

def domain_get(request, domain_id):
    manager = keystoneclient(request, admin=True).domains
    return manager.get(domain_id)

def get_default_domain(request):
    """Gets the default domain object to use when creating Identity object.

    Returns the domain context if is set, otherwise return the domain
    of the logon user.
    """
    domain_id = request.session.get("domain_context", None)
    domain_name = request.session.get("domain_context_name", None)
    # if running in Keystone V3 or later
    if VERSIONS.active >= 3 and not domain_id:
        # if no domain context set, default to users' domain
        domain_id = request.user.user_domain_id
        try:
            domain = domain_get(request, domain_id)
            domain_name = domain.name
        except Exception:
            LOG.warning("Unable to retrieve Domain: %s" % domain_id)
    domain = base.APIDictWrapper({"id": domain_id,
                                  "name": domain_name})
    return domain

def tenant_create(request, name, description=None, enabled=None,
                  domain=None, **kwargs):
    manager = VERSIONS.get_project_manager(request, admin=True)
    if VERSIONS.active < 3:
        return manager.create(name, description, enabled, **kwargs)
    else:
        return manager.create(name, domain,
                              description=description,
                              enabled=enabled, **kwargs)

def user_create(request, name=None, email=None, password=None, project=None,
                enabled=None, domain=None):
    manager = keystoneclient(request, admin=True).users
    try:
        if VERSIONS.active < 3:
            user = manager.create(name, password, email, project, enabled)
            return VERSIONS.upgrade_v2_user(user)
        else:
            return manager.create(name, password=password, email=email,
                                  project=project, enabled=enabled,
                                  domain=domain)
    except keystone_exceptions.Conflict:
        raise exceptions.Conflict()

def user_update_password(request, user, password, admin=True):

    if not keystone_can_edit_user():
        raise keystone_exceptions.ClientException(
            405, _("Identity service does not allow editing user password."))

    manager = keystoneclient(request, admin=admin).users
    if VERSIONS.active < 3:
        return manager.update_password(user, password)
    else:
        return manager.update(user, password=password)

def user_get_by_name(request, username):
    kwargs = {'name': username}
    user = keystoneclient(request, admin=True).users.user_get_by_name(
        username=username)
    return VERSIONS.upgrade_v2_user(user)


#################
# NOVA
#################
from novaclient.v2 import daolinets
from openstack_dashboard.api import nova as nova_api

@memoized
def novaclient(request):
    c = nova_api.novaclient(request)
    c.daolinets = daolinets.NetworkManager(c)
    return c

def network_list(request):
    return novaclient(request).networks.list()

def group_list(request):
    return novaclient(request).daolinets.group_list()

def group_get(request, id):
    return novaclient(request).daolinets.group_get(id)

def group_create(request, name=None, description=None, project_id=None):
    if project_id is None:
        project_id = request.user.tenant_id

    return novaclient(request).daolinets.group_create(
        name=name, description=description, project_id=project_id)

def group_delete(request, id):
    novaclient(request).daolinets.group_delete(id)

def group_update(request, group_id, **kwargs):
    return novaclient(request).daolinets.group_update(group_id, **kwargs)

def group_member_get(request, group_id):
    return novaclient(request).daolinets.group_member_get(group_id)

def group_member_update(request, group_id, instance_id=None,
                        action=None):
    novaclient(request).daolinets.group_member_update(
        group_id, instance_id=instance_id, action=action)

def gateway_list(request):
    return novaclient(request).daolinets.gateway_list()

def firewall_get(request, instance):
    manager = novaclient(request).daolinets
    return manager.firewall_get_by_instance(instance)

def firewall_create(request, instance_id=None, hostname=None,
                    gateway_port=None, service_port=None):
    return novaclient(request).daolinets.firewall_create(
            instance_id=instance_id, hostname=hostname,
            gateway_port=gateway_port, service_port=service_port)

def firewall_delete(request, firewall_id):
    novaclient(request).daolinets.firewall_delete(firewall_id)

def firewall_exist(request, instance, hostname=None, gateway_port=None):
    return novaclient(request).daolinets.firewall_exists(
        instance, hostname=hostname, gateway_port=gateway_port)

# Deprecated
def singroup_list(request):
    return novaclient(request).daolinets.singroup_list()

def singroup_update(request, action=None, start=None, end=None):
    novaclient(request).daolinets.singroup_update(
        request.user.tenant_id, action=action, start=start, end=end)
