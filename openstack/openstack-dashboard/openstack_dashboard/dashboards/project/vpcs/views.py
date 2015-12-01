"""
Views for managing vpcs.
"""
import collections
import json
import logging
import random

from django.http import HttpResponse
from django.utils.datastructures import SortedDict
from django.utils.text import normalize_newlines
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from horizon import exceptions
from horizon.utils import memoized

from openstack_dashboard import api

from openstack_dashboard.dashboards.project.instances \
    import utils as instance_utils

LOG = logging.getLogger(__name__)

UNKNOWN = "UNKNOWN"
CONTAINERS = ["ssh", "wordpress", "mysql", "python", "php", "perl",
              "ruby", "java", "go", "apache" "tomcat", "nginx"]

class IndexView(generic.TemplateView):
    template_name = 'project/vpcs/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        try:
            networks = api.daolicloud.network_list(self.request)
        except Exception:
            networks = []
            exceptions.handle(self.request,
                              _('Unable to retrieve networks.'))
        #network_list = [(network.id, network.cidr) for network in networks]
        #network_list.sort()

        context['networks'] = networks
        context['vm_images'], context['container_images'] = get_images(self.request)
        return context

def get_images(request):
    try:
        images, more, prev = api.glance.image_list_detailed(
            request)
    except Exception:
        images = []
        exceptions.handle(request, ignore=True)

    vm_images = []
    container_images = []
    for image in images:
        img = {'id': image.id, 'name': image.name}
        if image.container_format in ('container', 'docker'):
            image_type = get_image_type(image)

            if image_type is None:
                continue

            img['type'] = image_type
            img['category'] = 'container'
            container_images.append(img)
        else:
            img['type'] = 'vm'
            img['category'] = img['type']
            vm_images.insert(0, img)

    return (vm_images, container_images)

def get_image_type(image):
    image_type = None

    for cs in CONTAINERS:
        if cs in image.name:
            image_type = cs
            break

    return image_type

def _get_servers(request):
    try:
        instances, has_more = api.nova.server_list(request)
    except Exception:
        instances = []
        exceptions.handle(request, _('Unable to retrieve instances.'))

    servers = []

    if instances:
        try:
            images, more, prev = api.glance.image_list_detailed(request)
        except Exception:
            images = []
            exceptions.handle(request, ignore=True)

        try:
            gateways = api.daolicloud.gateway_list(request)
        except Exception:
            gateways = []
            exceptions.handle(request, ignore=True)

        image_map = SortedDict([(str(image.id), image)
                                for image in images])
        gateway_map = SortedDict([(gateway.hostname, gateway.vext_ip)
                                  for gateway in gateways])


        for instance in instances:
            if hasattr(instance, 'image'):
                if isinstance(instance.image, dict):
                    if instance.image.get('id') in image_map:
                        instance.image = image_map[instance.image['id']]

            instance.full_firewalls = [firewall.to_dict() for firewall in
                api.daolicloud.firewall_get(request, instance.id)]

            for firewall in instance.full_firewalls:
                firewall['gateway_ip'] = gateway_map.get(firewall['hostname'])

            servers.append(server_format(request, instance))

    return servers

def server_format(request, instance):
    addresses = []

    for addrs in instance.addresses.values():
        for addr in addrs:
            addresses.append(addr['addr'])

    zone = getattr(instance, "OS-EXT-AZ:availability_zone")

    server = {"id": instance.id,
              "name": instance.name,
              "pid": instance.tenant_id,
              "ip": '|'.join(addresses),
              "dc": zone,
              "zone_name": zone,
              "status": instance.status,
              "firewalls": instance.full_firewalls,
              "type": UNKNOWN,
              "category": UNKNOWN,
              "gip": None,
              "port": None}

    if hasattr(instance, 'image'):
        image_type = get_image_type(instance.image)

        if image_type is not None:
            server['category'] = 'container'
    else:
        image_type = None

    server['type'] = image_type

    return server

def get_servers(request):
    ids = request.POST.getlist("ids")
    if not ids:
        ids = request.POST.getlist('ids[]')

    if not ids:
        return HttpResponse(json.dumps([]),
                            content_type='application/json')

    data = [s for s in _get_servers(request) if s['id'] in ids]

    return HttpResponse(json.dumps(data), content_type='application/json')

def get(request, instance_id):
    instance = api.nova.server_get(request, instance_id)
 
    try:
        gateways = api.daolicloud.gateway_list(request)
    except Exception:
        gateways = []
        exceptions.handle(request, ignore=True)

    instance.image = api.glance.image_get(request, instance.image['id'])
    gateway_map = SortedDict([(gateway.hostname, gateway.vext_ip)
                              for gateway in gateways])

    instance.full_firewalls = [firewall.to_dict() for firewall in
        api.daolicloud.firewall_get(request, instance.id)]

    for firewall in instance.full_firewalls:
        firewall['gateway_ip'] = gateway_map.get(firewall['hostname'])

    return HttpResponse(json.dumps(server_format(request, instance)),
                        content_type='application/json')

def show(request):
    try:
        groups = api.daolicloud.singroup_list(request)
    except Exception:
        groups = []
        exceptions.handle(request, _('Unable to retrieve vpcs.'))

    _groups = collections.defaultdict(list)

    for group in groups:
        _groups[group.start].append(group.end)
        _groups[group.end].append(group.start)

    data = {"servers": _get_servers(request),
            "groups": _groups}
    resp = HttpResponse(content_type='application/json')
    resp.write(json.dumps(data))
    resp.flush()
    return resp

def create(request):
    api.daolicloud.singroup_update(request,
                                   action='create',
                                   start=request.GET['suid'],
                                   end=request.GET['duid'])
    return HttpResponse(status=204)

def delete(request):
    api.daolicloud.singroup_update(request,
                                   action='delete',
                                   start=request.GET['suid'],
                                   end=request.GET['duid'])
    return HttpResponse(status=204)
