
class PortState(dict):
    def __init__(self):
        super(PortState, self).__init__()

    def add(self, port):
        self[port.port_no] = self[port.name] = port

    def remove(self, port):
        if self.has_key(port.port_no):
            del self[port.port_no]
        if self.has_key(port.name):
            del self[port.name]

class GatewayState(dict):
    def __init__(self, gateways):
        super(GatewayState, self).__init__()
        (self.add(g) for g in gateways)

    def add(self, gateway):
        self[gateway.datapath_id] = self[gateway.hostname] = gateway

class HashPort:
    def __init__(self):
        self._ports = {}

    def keys(self):
        return self._ports.keys()

    def has_key(self, key):
        return self._ports.has_key(key)

    def get(self, key):
        return self._ports.get(key)

    def set(self, key, value):
        self._ports[key] = value

    def update(self, key, value):
        self.set(key, value)

    def remove(self, key):
        try:
            del self._ports[key]
        except KeyError:
            pass

    def clear(self):
        self._ports.clear()

    def __len__(self):
        return len(self._ports)
