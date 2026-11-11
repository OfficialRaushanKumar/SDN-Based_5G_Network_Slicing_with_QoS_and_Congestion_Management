# Architecture and assignment design

## Planes and interfaces

- **Application plane:** `config/slices.json` is the slice intent interface. The validated loader checks identities, unique pairs/queues, rate bounds and total minimum capacity. This is a local configuration northbound interface, not a REST service.
- **Control plane:** `sdn_slicing/controller.py` is a Ryu OpenFlow 1.3 application. On switch connection, it installs explicit IPv4 forwarding entries for both directions of each pair. At the source switch it applies `set_queue(queue_id)` before output to trunk port 4; at the destination switch it sends matching packets to that destination host's access port. Proxy ARP handles address resolution for the fixed topology.
- **Data plane:** two Open vSwitch switches connect six hosts and one shared 100 Mbps trunk. Three Linux HTB queues are attached to each trunk egress. This provides queue-level bandwidth policies for the shared link.

The assignment lists OpenFlow, NETCONF and P4Runtime as southbound possibilities. This demo implements OpenFlow 1.3 through Ryu and OVS. It does not implement NETCONF or P4Runtime. The assignment also mentions meters; queue min/max rates are implemented here, but no OpenFlow meter table is configured.

The OVS queue/QoS configuration and OpenFlow queue selection follow the [Open vSwitch QoS guide](https://docs.openvswitch.org/en/stable/faq/qos/). HTB queue priority semantics are documented in the [Open vSwitch database schema manual](https://www.openvswitch.org/support/dist-docs/ovs-vswitchd.conf.db.5.html).

## Proposed service requirements

The PDF asks for differentiated bandwidth, latency and isolation; it sets no numeric rates. This lab proposes broadband 50–80 Mbps (best effort), healthcare 20–30 Mbps (10 ms objective, highest queue priority), and IoT 10–20 Mbps (100 ms objective). Their minimum sum is 80 Mbps, leaving 20 Mbps headroom under a proposed 100 Mbps link. Numbers are editable in the config. Delay objectives are goals to measure, not guarantees.

## Question i: how SDN supports the slices

The application records per-service intent. The controller converts each endpoint pair into forwarding rules and a queue selection at the shared link. OVS continues to forward packets in its data plane while applying the configured queue policy. Logical service flows therefore share physical infrastructure with different treatment.

## Question ii: enforcement and isolation

IPv4 source and destination addresses identify the three configured pairs. Explicit rules on both switches forward each flow only toward its peer. Queue actions are applied only when a packet leaves the source switch toward the trunk; unrelated flows receive no slice queue action and no explicit forwarding rule. Each slice has its own HTB queue on both trunk egress directions, with configured min and max rates. Queue priority is passed to the Linux HTB class (lower number has higher priority in this proposal). The controller does not currently perform admission control or dynamically reconfigure queue state.

Isolation here means distinct match/action policy and a separate scheduler queue with a rate ceiling; it is not cryptographic or tenant security isolation. Latency depends on link delay, queue backlog, packet sizes, host load and VM scheduling in addition to queue priority.

## Question iii: congestion response

Healthcare receives the highest proposed priority and 20 Mbps minimum; broadband can use up to 80 Mbps and yields capacity when constrained; IoT has a configured 10 Mbps minimum to avoid starvation and a 20 Mbps cap. HTB behavior and actual delivery must be inspected under simultaneous load. These settings are not a hard end-to-end latency SLA.
