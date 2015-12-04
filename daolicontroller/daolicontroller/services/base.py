"""Packet base class."""

import abc
import six

from oslo_config import cfg

from daolicontroller.lib import REDIRECT_TABLE

CONF = cfg.CONF

@six.add_metaclass(abc.ABCMeta)
class PacketBase(object):
    priority = 0

    def __init__(self, manager, ryuapp):
        self.manager = manager
        self.db = manager.db
        self.ryuapp = ryuapp

    def gateway_get(self, id):
        return self.manager.gateway[id]

    @abc.abstractmethod
    def run(self, *args, **kwargs):
        """Run the service of dealing packet in."""
        pass
        
    def port_get(self, dp, devname=None):
        if self.ryuapp.port_state.has_key(dp.id):
            return self.ryuapp.port_state[dp.id].get(devname)

    def ofp_get(self, dp):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        ofp_set = ofp_parser.OFPActionSetField
        ofp_out = ofp_parser.OFPActionOutput
        return (ofp, ofp_parser, ofp_set, ofp_out)

    def packet_out(self, msg, dp, actions, in_port=None):
        ofproto = dp.ofproto
        parser = dp.ofproto_parser

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        if in_port is None:
            in_port = msg.match['in_port']

        out = parser.OFPPacketOut(
            datapath=dp, buffer_id=msg.buffer_id,
            in_port=in_port, actions=actions, data=data)

        dp.send_msg(out)

    def redirect(self, msg, dp, **kwargs):
        ofproto = dp.ofproto
        parser = dp.ofproto_parser
        match = parser.OFPMatch(**kwargs)
        inst = [parser.OFPInstructionGotoTable(REDIRECT_TABLE)]

        self.add_flow(dp, match=match, inst=inst)

        actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        self.packet_out(msg, dp, actions)

    def add_flow(self, dp, match=None, actions=None, table_id=0,
                 idle_timeout=None, priority=None, inst=None):
        ofproto = dp.ofproto
        parser = dp.ofproto_parser

        if idle_timeout is None:
            idle_timeout = CONF.timeout

        if match is None:
            match = parser.OFPMatch()

        if inst is None:
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                                 actions)]

        mod = parser.OFPFlowMod(datapath=dp, command=ofproto.OFPFC_ADD,
                                table_id=table_id, idle_timeout=idle_timeout,
                                priority=priority or self.priority,
                                #buffer_id=ofproto.OFP_NO_BUFFER,
                                match=match, instructions=inst)
        dp.send_msg(mod)

    def delete_flow(self, dp, match, table_id=0):
        ofproto = dp.ofproto
        parser = dp.ofproto_parser
        
        mod = parser.OFPFlowMod(datapath=dp, table_id=table_id,
                                command=ofproto.OFPFC_DELETE,
                                out_port=ofproto.OFPP_ANY,
                                out_group=ofproto.OFPP_ANY,
                                match=match)
        dp.send_msg(mod)
