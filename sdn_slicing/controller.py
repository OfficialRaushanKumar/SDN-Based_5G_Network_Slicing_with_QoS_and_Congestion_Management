"""Ryu OpenFlow 1.3 controller for the fixed two-switch demo topology."""
import json
import logging
import sys
from pathlib import Path
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp, ipv4

LOG = logging.getLogger("slicing")
CONFIG = Path(__file__).resolve().parents[1] / "config" / "slices.json"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sdn_slicing.config import validate_config
HOSTS = {f"h{i}": {"ip": f"10.0.0.{i}", "mac": f"00:00:00:00:00:{i:02x}", "switch": 1 if i % 2 else 2, "port": (i + 1) // 2} for i in range(1, 7)}


class SlicingController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with CONFIG.open(encoding="utf-8") as stream:
            config = json.load(stream)
        validate_config(config)
        self.slices = config["slices"]

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features(self, ev):
        dp, p = ev.msg.datapath, ev.msg.datapath.ofproto
        parser = dp.ofproto_parser
        # Table miss sends ARP/unknown traffic to the controller; configured IPv4 flows are explicit.
        dp.send_msg(parser.OFPFlowMod(datapath=dp, priority=0, match=parser.OFPMatch(), instructions=[parser.OFPInstructionActions(p.OFPIT_APPLY_ACTIONS, [parser.OFPActionOutput(p.OFPP_CONTROLLER, p.OFPCML_NO_BUFFER)])]))
        for item in self.slices:
            a, b = HOSTS[item["src_host"]], HOSTS[item["dst_host"]]
            self._install_pair(dp, a, b, item)
        LOG.info("Installed static slice forwarding on switch %s", dp.id)

    def _install_pair(self, dp, a, b, item):
        if dp.id not in (a["switch"], b["switch"]):
            return
        p, parser = dp.ofproto, dp.ofproto_parser
        trunk_port = 4  # three access links are created before the s1-s2 link
        for src, dst in ((a, b), (b, a)):
            if dp.id not in (src["switch"], dst["switch"]):
                continue
            match = parser.OFPMatch(eth_type=0x0800, ipv4_src=src["ip"], ipv4_dst=dst["ip"])
            actions = []
            if dp.id == src["switch"]:
                actions.append(parser.OFPActionSetQueue(item["queue_id"]))
                out_port = trunk_port
            else:
                out_port = dst["port"]
            actions.append(parser.OFPActionOutput(out_port))
            dp.send_msg(parser.OFPFlowMod(datapath=dp, priority=200, match=match, instructions=[parser.OFPInstructionActions(p.OFPIT_APPLY_ACTIONS, actions)]))

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in(self, ev):
        msg, dp = ev.msg, ev.msg.datapath
        data = msg.data
        pkt = packet.Packet(data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth is None or eth.ethertype != 0x0806:
            return
        arp_pkt = pkt.get_protocol(arp.arp)
        if arp_pkt is None:
            return
        # Proxy ARP for the known /24 endpoints; response leaves through the requesting access port.
        target = next((h for h in HOSTS.values() if h["ip"] == arp_pkt.dst_ip), None)
        if target is None:
            return
        out_port = msg.match["in_port"]
        response = packet.Packet()
        response.add_protocol(ethernet.ethernet(dst=eth.src, src=target["mac"], ethertype=0x0806))
        response.add_protocol(arp.arp(opcode=arp.ARP_REPLY, src_mac=target["mac"], src_ip=target["ip"], dst_mac=eth.src, dst_ip=arp_pkt.src_ip))
        response.serialize()
        dp.send_msg(dp.ofproto_parser.OFPPacketOut(datapath=dp, buffer_id=dp.ofproto.OFP_NO_BUFFER, in_port=dp.ofproto.OFPP_CONTROLLER, actions=[dp.ofproto_parser.OFPActionOutput(out_port)], data=response.data))
