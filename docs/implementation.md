# Implementation notes

## Files

- `config/slices.json`: single source for link and service rates, host pairs, queue IDs and objectives.
- `sdn_slicing/config.py`: JSON loader and validation of exactly three unique pairs, queue IDs and feasible rates.
- `sdn_slicing/classifier.py`: small bidirectional pair lookup helper used in unit tests and available to tooling.
- `sdn_slicing/topology.py`: six Mininet hosts, two OVS switches and one shared TCLink trunk.
- `sdn_slicing/controller.py`: Ryu OpenFlow 1.3 rules, queue actions on trunk egress and proxy ARP.
- `scripts/setup_qos.sh`: creates one Linux HTB QoS object containing all three Queue records on trunk port 4 of each switch. Numeric HTB priority 1 is highest in this proposed configuration.
- `scripts/run_experiment.py`: starts topology, applies QoS, launches simultaneous TCP clients and healthcare ping, follows with simultaneous UDP probes for packet loss/jitter, and saves measured JSON/CSV.
- `scripts/plot_results.py`: creates a throughput comparison image from actual result CSV files when Matplotlib is installed.
- `scripts/start_controller.sh`, `start_topology.sh`, `install_ubuntu.sh`, `cleanup.sh`: lifecycle helpers.
- `tests/`: unit/source/schema checks; these do not prove a live OVS experiment works.

## Packet workflow

1. A host ARPs for the peer. The Ryu app replies with the fixed peer MAC through proxy ARP.
2. IPv4 packets match a source/destination rule at the source-side switch.
3. `OFPActionSetQueue` selects the pair's configured queue, followed by output to the s1-s2 trunk.
4. The destination-side switch matches the same IPv4 pair and outputs to the peer access port.
5. The reverse pair has symmetric rules and selects the same queue when it enters the trunk in the opposite direction.

The topology creates three access ports before the trunk on each switch, making the trunk port 4. If topology construction changes, update the controller and shell setup assumptions and inspect `ovs-ofctl show` output.

## Setup and versions

Use Ubuntu 22.04/24.04 with Mininet and OVS from Ubuntu packages. Ryu 4.34 is legacy software; use a Python 3.10/3.11 venv. Ryu is started separately from Mininet. For an interactive topology, start the controller, then run `sudo python3 sdn_slicing/topology.py`. For automated simultaneous measurements, use `sudo python3 scripts/run_experiment.py 20` while the controller is active.

## Queue units and result interpretation

The config stores rates in Mbps; the setup script converts them to bits per second for OVS `other-config:min-rate` / `max-rate`. These are scheduler settings on each egress trunk, not measured results. The experiment records iperf3 receiver throughput and sender retransmit count (a TCP congestion indicator, not packet loss percentage), plus ping RTT summary. Result files are generated only by live runs.
