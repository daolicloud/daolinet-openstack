import random
import netaddr
import six.moves.urllib.parse as urlparse

def get_shortened_ipv6(address):
    addr = netaddr.IPAddress(address, version=6)
    return str(addr.ipv6())

def replace_url(url, host=None, port=None, path=None):
    o = urlparse.urlparse(url)
    _host = o.hostname
    _port = o.port
    _path = o.path

    if host is not None:
        _host = host

    if port is not None:
        _port = port

    netloc = _host

    if _port is not None:
        netloc = ':'.join([netloc, str(_port)])

    if path is not None:
        _path = path

    return '%s://%s%s' % (o.scheme, netloc, _path)

def generate_seq():
    return random.randint(1000000000, 4294967296)
