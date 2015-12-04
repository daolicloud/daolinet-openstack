import os
import sys
import six
import copy

from eventlet import greenthread
from oslo_config import cfg
from oslo_log import log as logging

from ryu.lib import dpid as dpid_lib
from ryu.lib import hub
from ryu.ofproto import ether
from ryu.ofproto import inet

from daolicontroller import exception
from daolicontroller.lib import BMAX
from daolicontroller.lib import FILTERS
from daolicontroller.lib import PORT_MIN, PORT_MAX
from daolicontroller.lib import PR_FIREWALL, PR_INTERNET
from daolicontroller.objects import HashPort
from daolicontroller.openstack.common import threadgroup
from daolicontroller.openstack.common import timeutils
from daolicontroller.services.base import PacketBase

port_opts = [
    cfg.ListOpt('static_ports', default=[],
                help='The static port range'),
    cfg.IntOpt('port_timeout', default=10,
               help='The timeout value of a port'),
    cfg.IntOpt('threads', default=10000,
               help='The threads number'),
    cfg.FloatOpt('threshold', default=0.8,
                 help='The threshold of port set'),
]

CONF = cfg.CONF
LOG = logging.getLogger(__name__)
CONF.register_opts(port_opts)

class PacketIPv4(PacketBase):
    priority = 1

    def __init__(self, manager, ryuapp):
        super(PacketIPv4, self).__init__(manager, ryuapp)
        self.hashport = HashPort()
        self.static_ports = CONF.static_ports

        self.tg = threadgroup.ThreadGroup(CONF.threads)
        self.tg.add_thread(self._port_clean)

    def _port_clean(self):
        while True:
            greenthread.sleep(CONF.port_timeout)
            for key in self.hashport.keys():
                val = self.hashport.get(key)
                if val and timeutils.is_older_than(val, CONF.port_timeout):
                    self.hashport.remove(key)

    def filter_port(self, port):
        # When the threshold is reached, reset port set
        amount = int((PORT_MAX - PORT_MIN) * CONF.threshold)
        if len(self.hashport) > amount:
            self.hashport.clear()

        while True:
            if port <= PORT_MIN:
                port = PORT_MAX - port
                continue

            if port >= PORT_MAX:
                port = PORT_MAX - port / 2
                continue

            if port in FILTERS or self.hashport.has_key(port):
                port += 1
                continue

            self.hashport.set(port, timeutils.utcnow())

            return port

    def _in_out_kwargs(self, pkt_ipv4, pkt_tp, ofp_set, src_port, dst_port=None):
        if pkt_ipv4.proto == inet.IPPROTO_TCP:
            inkwargs = {'tcp_src': pkt_tp.dst_port,
                        'tcp_dst': pkt_tp.src_port}
            outkwargs = {'tcp_src': pkt_tp.src_port,
                         'tcp_dst': pkt_tp.dst_port}

            mod_inkwargs = {'tcp_dst': src_port}
            mod_outkwargs = {'tcp_src': src_port}

            if dst_port is not None:
                mod_inkwargs['tcp_src'] = dst_port
                mod_outkwargs['tcp_dst'] = dst_port

        elif pkt_ipv4.proto == inet.IPPROTO_UDP:
            inkwargs = {'udp_src': pkt_tp.dst_port,
                        'udp_dst': pkt_tp.src_port}
            outkwargs = {'udp_src': pkt_tp.src_port,
                         'udp_dst': pkt_tp.dst_port}

            mod_inkwargs = {'udp_dst': src_port}
            mod_outkwargs = {'udp_src': src_port}

            if dst_port is not None:
                mod_inkwargs['udp_src'] = dst_port
                mod_outkwargs['udp_dst'] = dst_port

        else:
            outkwargs = inkwargs = {'icmpv4_id': pkt_tp.id}
            mod_inkwargs = mod_outkwargs = {'icmpv4_id': src_port}

        return (inkwargs, outkwargs, mod_inkwargs, mod_outkwargs)

    def _in_out_keys(self, pkt_ipv4, pkt_tp, ofp_set, src_port, dst_port=None):
        if pkt_ipv4.proto == inet.IPPROTO_TCP:
            inkeys = [ofp_set(tcp_src=pkt_tp.dst_port),
                      ofp_set(tcp_dst=pkt_tp.src_port)]
            outkeys = [ofp_set(tcp_src=pkt_tp.src_port),
                       ofp_set(tcp_dst=pkt_tp.dst_port)]

            mod_inkeys = [ofp_set(tcp_dst=src_port)]
            mod_outkeys = [ofp_set(tcp_src=src_port)]

            if dst_port is not None:
                mod_inkeys.append(ofp_set(tcp_src=dst_port))
                mod_outkeys.append(ofp_set(tcp_dst=dst_port))

        elif pkt_ipv4.proto == inet.IPPROTO_UDP:
            inkeys = [ofp_set(udp_src=pkt_tp.dst_port),
                      ofp_set(udp_dst=pkt_tp.src_port)]
            outkeys = [ofp_set(udp_src=pkt_tp.src_port),
                       ofp_set(udp_dst=pkt_tp.dst_port)]

            mod_inkeys = [ofp_set(udp_dst=src_port)]
            mod_outkeys = [ofp_set(udp_src=src_port)]

            if dst_port is not None:
                mod_inkeys.append(ofp_set(udp_src=dst_port))
                mod_outkeys.append(ofp_set(udp_dst=dst_port))
        else:
            inkeys = [ofp_set(icmpv4_id=pkt_tp.id)]
            outkeys = inkeys

            mod_inkeys = [ofp_set(icmpv4_id=src_port)]

            if dst_port is not None:
                mod_inkeys.append(ofp_set(icmpv4_id=dst_port))

            mod_outkeys = mod_inkeys

        return (inkeys, outkeys, mod_inkeys, mod_outkeys)

    def setup_ip_flow(self, msg, dp, in_port, src_key, pkt_ether, pkt_ipv4, pkt_tp,
                      src, src_gateway, dst, dst_gateway,
                      priority=PR_INTERNET):
        ofp, ofp_parser, ofp_set, ofp_out = self.ofp_get(dp)
        liport = self.port_get(dp, devname=src_gateway['int_dev']).port_no

        rdp = self.ryuapp.dps[dpid_lib.str_to_dpid(dst_gateway['datapath_id'])]
        rofp, rofp_parser, rofp_set, rofp_out = self.ofp_get(rdp)
        riport = self.port_get(rdp, devname=dst_gateway['int_dev']).port_no

        server_port = self.port_get(rdp, dst.devname)
        if not server_port:
            return

        port_len = len(self.static_ports)

        if port_len == 0:
            port = None
        else:
            port = self.static_ports[pkt_ipv4.identification % port_len]

        inkeys, outkeys, mod_inkeys, mod_outkeys = self._in_out_keys(
                pkt_ipv4, pkt_tp, ofp_set, src_key, port)

        inkwargs, outkwargs, mod_inkwargs, mod_outkwargs = self._in_out_kwargs(
                pkt_ipv4, pkt_tp, ofp_set, src_key, port)

        if pkt_ether.dst == dst.mac_address:
            dst_srcmac = src.mac_address
        else:
            dst_srcmac = dst_gateway['vint_mac']

        if src_gateway['idc_id'] == dst_gateway['idc_id']:
            output_local_actions = [
                    ofp_set(eth_src=src_gateway['int_mac']),
                    ofp_set(eth_dst=dst_gateway['int_mac']),
                    ofp_set(ipv4_src=src_gateway['int_ip']),
                    ofp_set(ipv4_dst=dst_gateway['int_ip'])]

            output_local_actions.extend(mod_outkeys)
            output_local_actions.append(ofp_out(liport))

            input_local_match = ofp_parser.OFPMatch(
                    in_port=liport,
                    eth_type=ether.ETH_TYPE_IP,
                    eth_dst=src_gateway['int_mac'],
                    ip_proto=pkt_ipv4.proto,
                    ipv4_src=dst_gateway['int_ip'],
                    ipv4_dst=src_gateway['int_ip'],
                    **mod_inkwargs)

            input_remote_match = rofp_parser.OFPMatch(
                    in_port=riport,
                    eth_type=ether.ETH_TYPE_IP,
                    eth_dst=dst_gateway['int_mac'],
                    ip_proto=pkt_ipv4.proto,
                    ipv4_src=src_gateway['int_ip'],
                    ipv4_dst=dst_gateway['int_ip'],
                    **mod_outkwargs)

            output_remote_actions = [
                    rofp_set(eth_src=dst_gateway['int_mac']),
                    rofp_set(eth_dst=src_gateway['int_mac']),
                    rofp_set(ipv4_src=dst_gateway['int_ip']),
                    rofp_set(ipv4_dst=src_gateway['int_ip'])]

            output_remote_actions.extend(mod_inkeys)
            output_remote_actions.append(rofp_out(riport))
        else:
            src_gateways = self.db.gateway_get_by_idc(src_gateway['idc_id'])
            dst_gateways = self.db.gateway_get_by_idc(dst_gateway['idc_id'])

            if not src_gateways or not dst_gateways:
                return

            src_dps = dict((g.datapath_id, g) for g in src_gateways)
            dst_dps = dict((g.datapath_id, g) for g in dst_gateways)

            lgdp_id = (src_gateways[pkt_ipv4.identification % len(src_gateways)]
                       if src_gateway.datapath_id not in src_dps else None)
            rgdp_id = (dst_gateways[pkt_ipv4.identification % len(dst_gateways)]
                       if dst_gateway.datapath_id not in dst_dps else None)

            input_remote_match, output_remote_actions = self._remote_gateway(
                    rdp, in_port, pkt_ether, pkt_ipv4, src_gateway, dst_gateway,
                    mod_inkeys, mod_inkwargs, mod_outkwargs,
                    riport=riport, lgdp_id=lgdp_id, rgdp_id=rgdp_id)

            input_local_match, output_local_actions = self._local_gateway(
                    dp, pkt_ether, pkt_ipv4, src_gateway, dst_gateway,
                    mod_outkeys, mod_inkwargs, mod_outkwargs,
                    liport=liport, lgdp_id=lgdp_id, rgdp_id=rgdp_id)

        output_remote_match, input_remote_actions = self._remote_host(rdp,
                server_port.port_no, pkt_ipv4, src, dst, dst_srcmac, outkeys,
                **inkwargs)

        output_local_match, input_local_actions = self._local_host(dp,
                in_port, pkt_ether, pkt_ipv4, inkeys, **outkwargs)

        self.add_flow(rdp, input_remote_match, input_remote_actions, priority=priority)
        self.add_flow(rdp, output_remote_match, output_remote_actions, priority=priority)

        self.add_flow(dp, input_local_match, input_local_actions, priority=priority)
        self.add_flow(dp, output_local_match, output_local_actions, priority=priority)
        self.packet_out(msg, dp, output_local_actions)

    def _redirect(self, msg, dp, in_port, pkt_ether, pkt_ipv4, output, **kwargs):
        ofp, ofp_parser, ofp_set, ofp_out = self.ofp_get(dp)
        match = ofp_parser.OFPMatch(
                in_port=in_port, eth_type=ether.ETH_TYPE_IP,
                ip_proto=pkt_ipv4.proto,
                eth_src=pkt_ether.src, eth_dst=pkt_ether.dst,
                ipv4_src=pkt_ipv4.src, ipv4_dst=pkt_ipv4.dst,
                **kwargs)

        actions = [ofp_parser.OFPActionOutput(output)]

        self.add_flow(dp, match, actions)
        self.packet_out(msg, dp, actions)

        return True


    def firewall(self, msg, dp, in_port, key, pkt_ether, pkt_ipv4, pkt_tp, gateway):
        ofp, ofp_parser, ofp_set, ofp_out = self.ofp_get(dp)

        inkwargs, outkwargs, _, _ = self._in_out_kwargs(
                    pkt_ipv4, pkt_tp, ofp_set, key)

        port = self.port_get(dp, devname=gateway.ext_dev)
        if not port:
            raise exception.DevicePortNotFound(device=gateway.ext_dev)

        if in_port == port.port_no:
            if pkt_ipv4.dst != gateway.ext_ip and \
                    pkt_ipv4.dst.rpartition('.')[2] != str(BMAX):
                raise exception.IPAddressNotMatch(address=pkt_ipv4.dst)

            # ICMP Packet redirect to physical host
            if pkt_ipv4.proto != inet.IPPROTO_ICMP:
                server = self.db.firewall_get_by_packet(gateway.hostname, pkt_tp.dst_port)
                if server:
                    self._firewall(msg, dp, in_port, pkt_ether, pkt_ipv4, pkt_tp, server, gateway)
                    return True

            return self._redirect(msg, dp, in_port, pkt_ether, pkt_ipv4,
                                  dp.ofproto.OFPP_LOCAL, **outkwargs)

        if gateway.int_dev != gateway.ext_dev:
            int_port = self.port_get(dp, devname=gateway.int_dev)
            tap_port = self.port_get(dp, devname=gateway.vint_dev)

            if not int_port or not tap_port:
                device = gateway.int_dev if not int_port else gateway.vint_dev
                raise exception.DevicePortNotFound(device=device)

            if in_port == int_port.port_no:
                if pkt_ipv4.dst != gateway.int_ip and \
                        pkt_ipv4.dst.rpartition('.')[2] != str(BMAX):
                    raise exception.IPAddressNotMatch(address=pkt_ipv4.dst)

                return self._redirect(msg, dp, in_port, pkt_ether, pkt_ipv4,
                                      tap_port.port_no, **outkwargs)

            if in_port == tap_port.port_no:
                if pkt_ipv4.src != gateway.int_ip:
                    raise exception.IPAddressNotMatch(address=pkt_ipv4.src)

                return self._redirect(msg, dp, in_port, pkt_ether, pkt_ipv4,
                                      int_port.port_no, **outkwargs)

        if in_port == dp.ofproto.OFPP_LOCAL:
            if pkt_ipv4.src != gateway['ext_ip']:
                raise exception.IPAddressNotMatch(address=pkt_ipv4.src)

            return self._redirect(msg, dp, in_port, pkt_ether, pkt_ipv4,
                                  port.port_no, **outkwargs)


    def _firewall(self, msg, dp, in_port, pkt_ether, pkt_ipv4, pkt_tp, server, gateway,
                  priority=PR_FIREWALL):
        ofp, ofp_parser, ofp_set, ofp_out = self.ofp_get(dp)

        if pkt_ipv4.proto == inet.IPPROTO_TCP:
            output_key = [ofp_set(tcp_src=pkt_tp.dst_port)]
            input_key = [ofp_set(tcp_dst=server.service_port)]
            output_kwargs = {
                'tcp_src': server.service_port,
                'tcp_dst': pkt_tp.src_port}
            input_kwargs = {
                'tcp_src': pkt_tp.src_port,
                'tcp_dst': server.service_port}
        else:
            output_key = [ofp_set(udp_src=pkt_tp.dst_port)]
            input_key = [ofp_set(udp_dst=server.service_port)]
            output_kwargs = {
                'udp_src': server.service_port,
                'udp_dst': pkt_tp.src_port}
            input_kwargs = {
                'udp_src': pkt_tp.src_port,
                'udp_dst': server.service_port}

        inkwargs, outkwargs = self._in_out_kwargs(
                pkt_ipv4, pkt_tp, ofp_set, None)[:2] ##

        input_match, output_actions = self._local_host(dp, in_port,
                pkt_ether, pkt_ipv4, output_key, **outkwargs)

        def server_port_wrap(dpath):
            server_port = self.port_get(dpath, server.devname)

            # Virtual machine may be poweroff
            if not server_port:
                raise exception.DevicePortNotFound(device=server.devname)

            return server_port


        if server.host == gateway.hostname:
            server_port = server_port_wrap(dp)

            input_actions = [
                    ofp_set(eth_src=gateway['vint_mac']),
                    ofp_set(eth_dst=server.mac_address),
                    ofp_set(ipv4_dst=server.address)]

            input_actions.extend(input_key)
            input_actions.append(ofp_out(server_port.port_no))

            output_match = ofp_parser.OFPMatch(
                    in_port=server_port.port_no,
                    eth_type=ether.ETH_TYPE_IP,
                    ip_proto=pkt_ipv4.proto,
                    ipv4_src=server.address,
                    ipv4_dst=pkt_ipv4.src,
                    **output_kwargs)
        else:
            server_gateway = self.gateway_get(server.host)
            ldp = self.ryuapp.dps[dpid_lib.str_to_dpid(server_gateway.datapath_id)]
            lofp, lofp_parser, lofp_set, lofp_out = self.ofp_get(ldp)
            liport = self.port_get(ldp, devname=server_gateway.int_dev).port_no
            server_port = server_port_wrap(ldp)

            giport = self.port_get(dp, devname=gateway['int_dev']).port_no

            input_actions = [
                    ofp_set(eth_src=gateway['int_mac']),
                    ofp_set(eth_dst=server_gateway.int_mac),
                    ofp_set(ipv4_src=gateway['int_ip']),
                    ofp_set(ipv4_dst=server_gateway.int_ip)]

            input_actions.extend(input_key)
            input_actions.append(ofp_out(giport))

            output_match = ofp_parser.OFPMatch(
                    in_port=giport,
                    eth_type=ether.ETH_TYPE_IP,
                    eth_dst=gateway['int_mac'],
                    ip_proto=pkt_ipv4.proto,
                    ipv4_src=server_gateway.int_ip,
                    ipv4_dst=gateway['int_ip'],
                    **output_kwargs)

            input_local_match = lofp_parser.OFPMatch(
                    in_port=liport,
                    eth_type=ether.ETH_TYPE_IP,
                    eth_dst=server_gateway.int_mac,
                    ip_proto=pkt_ipv4.proto,
                    ipv4_src=gateway['int_ip'],
                    ipv4_dst=server_gateway.int_ip,
                    **input_kwargs)

            input_local_actions = [
                    lofp_set(eth_src=server_gateway.vint_mac),
                    lofp_set(eth_dst=server.mac_address),
                    lofp_set(ipv4_src=pkt_ipv4.src),
                    lofp_set(ipv4_dst=server.address),
                    lofp_out(server_port.port_no)]

            output_local_match = lofp_parser.OFPMatch(
                    in_port=server_port.port_no,
                    eth_type=ether.ETH_TYPE_IP,
                    eth_src=server.mac_address,
                    ip_proto=pkt_ipv4.proto,
                    ipv4_src=servernstance.address,
                    ipv4_dst=pkt_ipv4.src,
                    **output_kwargs)

            output_local_actions = [
                    lofp_set(eth_src=server_gateway.int_mac),
                    lofp_set(eth_dst=gateway['int_mac']),
                    lofp_set(ipv4_src=server_gateway.int_ip),
                    lofp_set(ipv4_dst=gateway['int_ip']),
                    ofp_out(liport)]

            self.add_flow(ldp, input_local_match, input_local_actions,
                          priority=priority)
            self.add_flow(ldp, output_local_match, output_local_actions,
                          priority=priority)

        self.add_flow(dp, output_match, output_actions, priority=priority)
        self.add_flow(dp, input_match, input_actions, priority=priority)
        #self.packet_out(msg, dp, input_actions)

    def _local_host(self, dp, in_port, pkt_ether, pkt_ipv4,
                    inkeys, **kwargs):
        ofp, ofp_parser, ofp_set, ofp_out = self.ofp_get(dp)

        output_match = ofp_parser.OFPMatch(
                in_port=in_port,
                eth_type=ether.ETH_TYPE_IP,
                eth_src=pkt_ether.src,
                ip_proto=pkt_ipv4.proto,
                ipv4_src=pkt_ipv4.src,
                ipv4_dst=pkt_ipv4.dst,
                **kwargs)

        input_actions = [
                ofp_set(eth_src=pkt_ether.dst),
                ofp_set(eth_dst=pkt_ether.src),
                ofp_set(ipv4_src=pkt_ipv4.dst),
                ofp_set(ipv4_dst=pkt_ipv4.src)]

        input_actions.extend(inkeys)
        input_actions.append(ofp_out(in_port))

        return (output_match, input_actions)

    def _local_gateway(self, dp, pkt_ether, pkt_ipv4, src_gateway, dst_gateway,
                       outkeys, mod_inkwargs, mod_outkwargs,
                       liport=None, lgdp_id=None, rgdp_id=None, public=False):
        ofp, ofp_parser, ofp_set, ofp_out = self.ofp_get(dp)

        if not public:
            if rgdp_id is None:
                ipv4_dst = dst_gateway.vext_ip
            else:
                if isinstance(lgdp_id, six.string_types):
                    remote_gateway = self.gateway_get(rgdp_id)
                else:
                    remote_gateway = rgdp_id
                ipv4_dst = remote_gateway.vext_ip
        else:
            ipv4_dst = pkt_ipv4.dst

        if lgdp_id is not None:
            if liport is None:
                liport = self.port_get(dp, devname=src_gateway.int_dev).port_no

            if isinstance(lgdp_id, six.string_types):
                local_gateway = self.gateway_get(lgdp_id)
                lgdp = self.ryuapp.dps[dpid_lib.str_to_dpid(lgdp_id)]
            else:
                local_gateway = lgdp_id
                lgdp = self.ryuapp.dps[dpid_lib.str_to_dpid(lgdp_id.datapath_id)]

            lgofp, lgofp_parser, lgofp_set, lgofp_out = self.ofp_get(lgdp)
            lgiport = self.port_get(lgdp, devname=local_gateway.int_dev).port_no
            lgeport = self.port_get(lgdp, devname=local_gateway.ext_dev).port_no

            input_match = ofp_parser.OFPMatch(
                    in_port=liport,
                    eth_type=ether.ETH_TYPE_IP,
                    eth_dst=src_gateway.int_mac,
                    ip_proto=pkt_ipv4.proto,
                    ipv4_src=local_gateway.int_ip,
                    ipv4_dst=src_gateway.int_ip,
                    **mod_inkwargs)

            output_actions = [
                    ofp_set(eth_src=src_gateway.int_mac),
                    ofp_set(eth_dst=local_gateway.int_mac),
                    ofp_set(ipv4_src=src_gateway.int_ip),
                    ofp_set(ipv4_dst=local_gateway.int_ip)]

            output_actions.extend(outkeys)
            output_actions.append(ofp_out(liport))

            input_gateway_match = lgofp_parser.OFPMatch(
                    in_port=lgeport,
                    eth_type=ether.ETH_TYPE_IP,
                    eth_dst=local_gateway.ext_mac,
                    ip_proto=pkt_ipv4.proto,
                    ipv4_src=ipv4_dst,
                    ipv4_dst=local_gateway.ext_ip,
                    **mod_inkwargs)

            input_gateway_actions = [
                    lgofp_set(eth_src=local_gateway.int_mac),
                    lgofp_set(eth_dst=src_gateway.int_mac),
                    lgofp_set(ipv4_src=local_gateway.int_ip),
                    lgofp_set(ipv4_dst=src_gateway.int_ip),
                    lgofp_out(lgiport)]

            output_gateway_match = lgofp_parser.OFPMatch(
                    in_port=lgiport,
                    eth_type=ether.ETH_TYPE_IP,
                    eth_dst=local_gateway.int_mac,
                    ip_proto=pkt_ipv4.proto,
                    ipv4_src=src_gateway.int_ip,
                    ipv4_dst=local_gateway.int_ip,
                    **mod_outkwargs)

            output_gateway_actions = [
                    lgofp_set(eth_src=local_gateway.ext_mac),
                    lgofp_set(eth_dst=local_gateway.idc_mac),
                    lgofp_set(ipv4_src=local_gateway.ext_ip),
                    lgofp_set(ipv4_dst=ipv4_dst),
                    lgofp_out(lgeport)]

            self.add_flow(lgdp, input_gateway_match, input_gateway_actions,
                          priority=PR_INTERNET)
            self.add_flow(lgdp, output_gateway_match, output_gateway_actions,
                          priority=PR_INTERNET)
        else: 
            leport = self.port_get(dp, devname=src_gateway.ext_dev).port_no

            input_match = ofp_parser.OFPMatch(
                    in_port=leport,
                    eth_type=ether.ETH_TYPE_IP,
                    eth_dst=src_gateway.ext_mac,
                    ip_proto=pkt_ipv4.proto,
                    ipv4_src=ipv4_dst,
                    ipv4_dst=src_gateway.ext_ip,
                    **mod_inkwargs)

            output_actions = [
                    ofp_set(eth_src=src_gateway.ext_mac),
                    ofp_set(eth_dst=src_gateway.idc_mac),
                    ofp_set(ipv4_src=src_gateway.ext_ip),
                    ofp_set(ipv4_dst=ipv4_dst)]

            output_actions.extend(outkeys)
            output_actions.append(ofp_out(leport))

        return (input_match, output_actions)

    def _remote_host(self, dp, in_port, pkt_ipv4, src, dst, dst_srcmac,
                     outkeys, **kwargs):
        ofp, ofp_parser, ofp_set, ofp_out = self.ofp_get(dp)

        output_match = ofp_parser.OFPMatch(
                in_port=in_port,
                eth_type=ether.ETH_TYPE_IP,
                eth_src=dst.mac_address,
                ip_proto=pkt_ipv4.proto,
                ipv4_src=dst.address,
                ipv4_dst=src.address,
                **kwargs)

        input_actions = [ofp_set(eth_src=dst_srcmac),
                         ofp_set(eth_dst=dst.mac_address),
                         ofp_set(ipv4_src=src.address),
                         ofp_set(ipv4_dst=dst.address)]

        input_actions.extend(outkeys)
        input_actions.append(ofp_out(in_port))

        return (output_match, input_actions)

    def _remote_gateway(self, dp, in_port, pkt_ether, pkt_ipv4, src_gateway, dst_gateway,
                        inkeys, mod_inkwargs, mod_outkwargs,
                        riport=None, lgdp_id=None, rgdp_id=None):
        ofp, ofp_parser, ofp_set, ofp_out = self.ofp_get(dp)

        if lgdp_id is None:
            ipv4_src = src_gateway.vext_ip
        else:
            if isinstance(lgdp_id, six.string_types):
                local_gateway = self.gateway_get(lgdp_id)
            else:
                local_gateway = lgdp_id
            ipv4_src = local_gateway.vext_ip

        if rgdp_id is not None:
            if riport is None:
                riport = self.port_get(dp, devname=dst_gateway.int_dev).port_no

            if isinstance(rgdp_id, six.string_types):
                remote_gateway = self.gateway_get(rgdp_id)
                rgdp = self.ryuapp.dps[dpid_lib.str_to_dpid(rgdp_id)]
            else:
                remote_gateway = rgdp_id
                rgdp = self.ryuapp.dps[dpid_lib.str_to_dpid(rgdp_id.datapath_id)]

            rgofp, rgofp_parser, rgofp_set, rgofp_out = self.ofp_get(rgdp)
            rgiport = self.port_get(rgdp, devname=remote_gateway.int_dev).port_no
            rgeport = self.port_get(rgdp, devname=remote_gateway.ext_dev).port_no

            input_gateway_match = rgofp_parser.OFPMatch(
                    in_port=rgeport,
                    eth_type=ether.ETH_TYPE_IP,
                    eth_dst=remote_gateway.ext_mac,
                    ip_proto=pkt_ipv4.proto,
                    ipv4_src=ipv4_src,
                    ipv4_dst=remote_gateway.ext_ip,
                    **mod_outkwargs)##

            input_gateway_actions = [
                    rgofp_set(eth_src=remote_gateway.int_mac),
                    rgofp_set(eth_dst=dst_gateway.int_mac),
                    rgofp_set(ipv4_src=remote_gateway.int_ip),
                    rgofp_set(ipv4_dst=dst_gateway.int_ip),
                    rgofp_out(rgiport)]

            output_gateway_match = rgofp_parser.OFPMatch(
                    in_port=rgiport,
                    eth_type=ether.ETH_TYPE_IP,
                    eth_dst=remote_gateway.int_mac,
                    ip_proto=pkt_ipv4.proto,
                    ipv4_src=dst_gateway.int_ip,
                    ipv4_dst=remote_gateway.int_ip,
                    **mod_inkwargs)##

            output_gateway_actions = [
                    rgofp_set(eth_src=remote_gateway.ext_mac),
                    rgofp_set(eth_dst=remote_gateway.idc_mac),
                    rgofp_set(ipv4_src=remote_gateway.ext_ip),
                    rgofp_set(ipv4_dst=ipv4_src),
                    rgofp_out(rgeport)]

            input_match = ofp_parser.OFPMatch(
                    in_port=riport,
                    eth_type=ether.ETH_TYPE_IP,
                    eth_dst=dst_gateway.int_mac,
                    ip_proto=pkt_ipv4.proto,
                    ipv4_src=remote_gateway.int_ip,
                    ipv4_dst=dst_gateway.int_ip,
                    **mod_outkwargs) ##

            output_actions =[
                    ofp_set(eth_src=dst_gateway.int_mac),
                    ofp_set(eth_dst=remote_gateway.int_mac),
                    ofp_set(ipv4_src=dst_gateway.int_ip),
                    ofp_set(ipv4_dst=remote_gateway.int_ip)]

            if inkeys is not None:
                output_actions.extend(inkeys)

            output_actions.append(ofp_out(riport))

            self.add_flow(rgdp, input_gateway_match, input_gateway_actions,
                          priority=PR_INTERNET)
            self.add_flow(rgdp, output_gateway_match, output_gateway_actions,
                          priority=PR_INTERNET)
        else:
            report = self.port_get(dp, devname=dst_gateway.ext_dev).port_no

            input_match = ofp_parser.OFPMatch(
                    in_port=report,
                    eth_type=ether.ETH_TYPE_IP,
                    eth_dst=dst_gateway.ext_mac,
                    ip_proto=pkt_ipv4.proto,
                    ipv4_src=ipv4_src,
                    ipv4_dst=dst_gateway.ext_ip,
                    **mod_outkwargs) ##

            output_actions = [
                    ofp_set(eth_src=dst_gateway.ext_mac),
                    ofp_set(eth_dst=dst_gateway.idc_mac),
                    ofp_set(ipv4_src=dst_gateway.ext_ip),
                    ofp_set(ipv4_dst=ipv4_src)]

            if inkeys is not None:
                output_actions.extend(inkeys)

            output_actions.append(ofp_out(report))

        return (input_match, output_actions)

    def run(self, msg, pkt_ether, pkt_ipv4, pkt_tp, src_gateway, **kwargs):
        dp = msg.datapath
        in_port = msg.match['in_port']

        if pkt_ipv4.proto == inet.IPPROTO_ICMP:
            src_key = self.filter_port(pkt_tp.id)
            #src_key = pkt_tp.id
        else:
            src_key = self.filter_port(pkt_tp.src_port)
            #src_key = pkt_tp.src_port

        try:
            ret = self.firewall(msg, dp, in_port, src_key, pkt_ether,
                                pkt_ipv4, pkt_tp, src_gateway)
            if ret:
                return True
        except (exception.DevicePortNotFound, exception.IPAddressNotMatch) as e:
            LOG.debug(e.message)
            return False

        servers = self.db.server_get_by_mac(pkt_ether.src, pkt_ipv4.dst)
        src, dst, has_more = (servers['src'], servers['dst'], servers['has_more'])

        if src is None or (dst is not None and not has_more):
            return False

        # Create nat flow if 'dst' instance is not null, else public flow
        if dst is not None:
            if src.host == dst.host:
                ofp, ofp_parser, ofp_set, ofp_out = self.ofp_get(dp)
                submac = (pkt_ether.dst if pkt_ether.dst != dst.mac_address
                                            else None)

                def same_host_flow(smac, dmac, sip, dip, iport, oport):
                    match = ofp_parser.OFPMatch(
                            in_port=iport,
                            eth_type=ether.ETH_TYPE_IP,
                            eth_src=smac,
                            ipv4_src=sip,
                            ipv4_dst=dip)
                    actions = ([ofp_set(eth_src=submac)] if submac is not None
                                                             else [])
                    actions += [ofp_set(eth_dst=dmac), ofp_out(oport)]
                    self.add_flow(dp, match, actions, priority=2)

                    return actions

                dst_port = self.port_get(dp, dst.devname).port_no
                same_host_flow(dst.mac_address, src.mac_address, pkt_ipv4.dst,
                               pkt_ipv4.src, dst_port, in_port)
                self.packet_out(msg, dp, same_host_flow(
                                src.mac_address, dst.mac_address, pkt_ipv4.src,
                                pkt_ipv4.dst, in_port, dst_port))
            else:
                dst_gateway = self.db.gateway_get_by_name(dst.host)

                self.setup_ip_flow(msg, dp, in_port, src_key, pkt_ether, pkt_ipv4,
                                   pkt_tp, src, src_gateway, dst, dst_gateway)
        else:
            self._public_ip(msg, dp, in_port, src_key, pkt_ether, pkt_ipv4, pkt_tp,
                            src, src_gateway)

    def _public_ip(self, msg, dp, in_port, src_key, pkt_ether, pkt_ipv4, pkt_tp,
                   src, src_gateway, priority=PR_INTERNET):
        ofp, ofp_parser, ofp_set, ofp_out = self.ofp_get(dp)

        inkwargs, outkwargs, mod_inkwargs, mod_outkwargs = self._in_out_kwargs(
                    pkt_ipv4, pkt_tp, ofp_set, src_key)

        if pkt_ipv4.proto == inet.IPPROTO_UDP and pkt_tp.dst_port == 67:
            gateway = src.address.split('.')
            gateway[2] = str(BMAX)
            gateway[3] = str(BMAX - 1)
            match = ofp_parser.OFPMatch(in_port=in_port,
                                        eth_type=ether.ETH_TYPE_IP,
                                        ip_proto=pkt_ipv4.proto,
                                        ipv4_src='.'.join(gateway),
                                        **outkwargs)
            actions = [ofp_set(eth_src=src_gateway['vint_mac']),
                       ofp_set(eth_dst=pkt_ether.src),
                       ofp_set(ipv4_src='.'.join(gateway)),
                       ofp_set(ipv4_dst=src.address),
                       ofp_set(udp_src=pkt_tp.dst_port),
                       ofp_set(udp_dst=pkt_tp.src_key),
                       ofp_out(ofp.OFPP_IN_PORT)]

            self.add_flow(dp, match, actions, priority=priority) 
            return self.packet_out(msg, dp, actions)

        greenthread.sleep(0)
        gateways = self.db.gateway_get_by_idc(src_gateway.idc_id)

        if gateways:
            gateway_dps = dict((g.datapath_id, g) for g in gateways)
            lgdp_id = (gateways[pkt_ipv4.identification % len(gateways)]
                       if src_gateway.datapath_id not in gateway_dps else None)

            inkeys, _, _, outkeys = self._in_out_keys(
                    pkt_ipv4, pkt_tp, ofp_set, src_key)

            input_match, output_actions = self._local_gateway(
                    dp, pkt_ether, pkt_ipv4, src_gateway, None,
                    outkeys, mod_inkwargs, mod_outkwargs, lgdp_id=lgdp_id,
                    public=True)

            output_match, input_actions = self._local_host(
                    dp, in_port, pkt_ether, pkt_ipv4, inkeys, **outkwargs)

            self.add_flow(dp, input_match, input_actions, priority=priority)
            self.add_flow(dp, output_match, output_actions, priority=priority)
            self.packet_out(msg, dp, output_actions)
        else:
            LOG.warn("Gateway not found - %s", src_gateway.hostname)
