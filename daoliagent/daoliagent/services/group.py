from oslo_config import cfg
from oslo_log import log as logging

from ryu.lib import dpid as dpid_lib
from ryu.ofproto import inet
from ryu.ofproto import ether

from daoliagent.lib import REDIRECT_GATEWAY_PORTS
from daoliagent.lib import REDIRECT_NORMAL_PORTS
from daoliagent.lib import REVERSE_GATEWAY_PORTS
from daoliagent.lib import REVERSE_NORMAL_PORTS
from daoliagent.services.base import PacketBase

port_opts = [
    cfg.ListOpt('normal_ports', default=[],
                help='The initial host port'),
    cfg.ListOpt('gateway_ports', default=[],
                help='The initial gateway port'),
    cfg.ListOpt('reverse_normal_ports', default=[],
                help='The initial reverse host port'),
    cfg.ListOpt('reverse_gateway_ports', default=[],
                help='The initial reverse gateway port'),
]

CONF = cfg.CONF
CONF.register_opts(port_opts)

LOG = logging.getLogger(__name__)

class PacketGroup(PacketBase):
    def __init__(self, manager, ryuapp):
        super(PacketGroup, self).__init__(manager, ryuapp)
        self.normal_ports = set(REDIRECT_NORMAL_PORTS) | \
                set(map(int, CONF.normal_ports))
        self.gateway_ports = set(REDIRECT_GATEWAY_PORTS) | \
                set(map(int, CONF.gateway_ports))
        self.reverse_normal_ports = set(REVERSE_NORMAL_PORTS) | \
                set(map(int, CONF.reverse_normal_ports))
        self.reverse_gateway_ports = set(REVERSE_GATEWAY_PORTS) | \
                set(map(int, CONF.reverse_gateway_ports))

    def init_flow(self, dp, gateway):
        ofp, ofp_parser, ofp_set, ofp_out = self.ofp_get(dp)
        server_port = self.port_get(dp, devname=gateway.ext_dev)

        if not server_port:
            return

        redirect_ports = self.normal_ports
        reverse_ports = self.reverse_normal_ports

        if gateway.ext_dev != gateway.int_dev:
            redirect_ports += self.gateway_ports
            reverse_ports += self.reverse_gateway_ports

        for port in redirect_ports:
            self.setup(dp, server_port.port_no, ofp_out(ofp.OFPP_LOCAL),
                       ipv4_dst=gateway.ext_ip, tcp_dst=port)
            self.setup(dp, ofp.OFPP_LOCAL, ofp_out(server_port.port_no),
                       ipv4_src=gateway.ext_ip, tcp_src=port)

        for port in reverse_ports:
            self.setup(dp, server_port.port_no, ofp_out(ofp.OFPP_LOCAL),
                       ipv4_dst=gateway.ext_ip, tcp_src=port)
            self.setup(dp, ofp.OFPP_LOCAL, ofp_out(server_port.port_no),
                       ipv4_src=gateway.ext_ip, tcp_dst=port)

        if gateway.vext_ip != gateway.ext_ip or gateway.ext_dev != gateway.int_dev:
            int_port = self.port_get(dp, devname=gateway.int_dev)
            tap_port = self.port_get(dp, devname=gateway.vint_dev)

            if not int_port or not tap_port:
                LOG.error("The device could not be found")
                return

            for port in self.gateway_ports:
                self.setup(dp, int_port.port_no, ofp_out(tap_port.port_no),
                           ipv4_dst=gateway.int_ip, tcp_dst=port)
                self.setup(dp, tap_port.port_no, ofp_out(int_port.port_no),
                           ipv4_src=gateway.int_ip, tcp_src=port)

            for port in self.reverse_gateway_ports:
                self.setup(dp, int_port.port_no, ofp_out(tap_port.port_no),
                           ipv4_dst=gateway.int_ip, tcp_src=port)
                self.setup(dp, tap_port.port_no, ofp_out(int_port.port_no),
                           ipv4_src=gateway.int_ip, tcp_dst=port)

    def setup(self, dp, in_port, out_port, **kwargs):
        match = dp.ofproto_parser.OFPMatch(
                in_port=in_port, eth_type=ether.ETH_TYPE_IP,
                ip_proto=inet.IPPROTO_TCP, **kwargs)

        self.add_flow(dp, match=match, actions=[out_port], idle_timeout=0)

    def run(self, src, src_gateway, dst, dst_gateway, **kwargs):
        sdp_id = dpid_lib.str_to_dpid(src_gateway['datapath_id'])
        ddp_id = dpid_lib.str_to_dpid(dst_gateway['datapath_id'])

        if self.ryuapp.dps.has_key(sdp_id):
            sdp = self.ryuapp.dps[sdp_id]
            sofp, sofp_parser, sofp_set, sofp_out = self.ofp_get(sdp)

            sport = self.port_get(sdp, src.devname)
            if sport:
                smatch = sofp_parser.OFPMatch(
                        in_port=sport.port_no,
                        eth_type=ether.ETH_TYPE_IP,
                        eth_src=src.mac_address,
                        ipv4_src=src.address,
                        ipv4_dst=dst.address)
                self.delete_flow(sdp, smatch)

        if self.ryuapp.dps.has_key(ddp_id):
            ddp = self.ryuapp.dps[ddp_id]
            dofp, dofp_parser, dofp_set, dofp_out = self.ofp_get(ddp)

            dport = self.port_get(ddp, dst.devname)
            if dport:
                dmatch = dofp_parser.OFPMatch(
                        in_port=dport.port_no,
                        eth_type=ether.ETH_TYPE_IP,
                        eth_src=dst.mac_address,
                        ipv4_src=dst.address,
                        ipv4_dst=src.address)
                self.delete_flow(ddp, dmatch)
