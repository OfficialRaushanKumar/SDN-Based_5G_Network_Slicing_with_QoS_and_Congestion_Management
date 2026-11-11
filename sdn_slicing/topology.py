"""Mininet topology: six hosts, two access switches, one shared trunk."""
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from config import load_config


class SlicingTopo(Topo):
    def build(self, capacity=100, delay="5ms"):
        left, right = self.addSwitch("s1", protocols="OpenFlow13"), self.addSwitch("s2", protocols="OpenFlow13")
        for idx in range(1, 7):
            host = self.addHost(f"h{idx}", ip=f"10.0.0.{idx}/24")
            access = left if idx % 2 else right
            self.addLink(host, access, bw=100)
        self.addLink(left, right, bw=capacity, delay=delay, use_htb=True)


def main():
    cfg = load_config()
    topo = SlicingTopo(capacity=cfg["link"]["capacity_mbps"], delay=f'{cfg["link"]["delay_ms"]}ms')
    net = Mininet(topo=topo, controller=None, switch=OVSSwitch, link=TCLink, autoSetMacs=True, build=True)
    net.addController("c0", controller=RemoteController, ip="127.0.0.1", port=6653)
    net.start()
    info("*** Hosts: h1↔h2 broadband, h3↔h4 healthcare, h5↔h6 IoT\n")
    info("*** Shared bottleneck: s1-s2; configure OVS queues with scripts/setup_qos.sh\n")
    try:
        CLI(net)
    finally:
        net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    main()
