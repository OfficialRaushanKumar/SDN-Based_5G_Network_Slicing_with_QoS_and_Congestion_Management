# SDN Based 5G Network Slicing with QoS and Congestion Management

**SRM Institute of Science and Technology, Kattankulathur** · **21CSE456T – Software Defined Networks** · Scenario Based Assessment · Academic Year 2026–27 (ODD)

This project demonstrates how an SDN controller can classify three service flows and apply different queue policies while they share one 100 Mbps transport link. It is a Mininet/Open vSwitch transport simulation. It is not a 5G core implementation and it does not establish that a real remote surgery system is safe.

## Problem and objectives

The assignment asks how SDN supports broadband, remote surgery and IoT slices; how bandwidth, latency and isolation needs are enforced; and what should happen under congestion. This project uses six Mininet hosts in three pairs, one shared switch-to-switch bottleneck, per-slice Open vSwitch queues, explicit OpenFlow 1.3 flows, concurrent iperf3, ping observations, and saved measurements.

## Requirements checklist and traceability

| PDF requirement | Implementation | Test / evidence | Documentation |
|---|---|---|---|
| Explain the three SDN slices | `docs/architecture.md` | `tests/test_config.py` | `README.md`, `docs/architecture.md` |
| Bandwidth, latency, isolation, enforcement | `config/slices.json`, `sdn_slicing/controller.py`, `scripts/setup_qos.sh` | `tests/test_config.py` | `docs/architecture.md` |
| Congestion behavior | `scripts/run_experiment.py` | Live Ubuntu measurement required | `docs/experiment_plan.md`, `docs/results_analysis.md` |
| Application slice manager and requests | `config/slices.json`, `sdn_slicing/config.py`, `scripts/show_slices.py` | `tests/test_config.py` | `docs/implementation.md` |
| Controller paths, queues and isolation | `sdn_slicing/controller.py` | Live OpenFlow integration required | `docs/implementation.md` |
| Queues and meters | `scripts/setup_qos.sh` configures queues; meters are not implemented | Live OVS inspection required | `docs/architecture.md` |
| Interfaces | Config file northbound; Ryu/OpenFlow 1.3 southbound | Live controller connection required | `docs/architecture.md` |
| Six hosts / three pairs / one bottleneck | `sdn_slicing/topology.py` | `tests/test_topology.py` | `docs/diagrams/topology.mmd` |
| Three queues with min/max rates | `config/slices.json`, `scripts/setup_qos.sh` | Live OVS queue inspection required | `docs/implementation.md` |
| Traffic mapping and concurrency | `sdn_slicing/controller.py`, `scripts/run_experiment.py` | Live Ubuntu run required | `docs/experiment_plan.md` |
| Show measured rates and flow config | Timestamped `results/` files; OVS inspection commands below | Live Ubuntu run required | `docs/results_analysis.md` |

The PDF does not prescribe numerical QoS values. Rates and latency objectives in `config/slices.json` are proposed, configurable lab parameters. Inspect the validated application-plane requests with `python3 scripts/show_slices.py`.

## Proposed slice policy

| Slice | Hosts | Min / max | Latency objective | Policy |
|---|---|---:|---|---|
| Broadband | h1 ↔ h2 | 50 / 80 Mbps | Best effort | Dedicated HTB queue, capped at 80 Mbps |
| Healthcare | h3 ↔ h4 | 20 / 30 Mbps | 10 ms objective (proposed) | Queue gets highest priority and 20 Mbps configured minimum |
| IoT | h5 ↔ h6 | 10 / 20 Mbps | 100 ms objective (proposed) | Dedicated queue retains a configured allocation and is capped |

The three minimum rates add to 80 Mbps, below the 100 Mbps trunk capacity. An HTB minimum is a scheduling guarantee under supported conditions, not bandwidth that can be delivered if the physical path or host cannot provide it. Queueing priority and rate settings alone do not guarantee end-to-end latency.

## Architecture

The application layer stores a slice intent in JSON. The Ryu control plane installs bidirectional IPv4 forwarding rules and selects each queue on trunk egress. Open vSwitch in the data plane schedules the packets through HTB queues. The switches proxy ARP for the fixed lab hosts. See [architecture](docs/architecture.md), [implementation details](docs/implementation.md), and [Mermaid diagrams](docs/diagrams/).

## Setup: Windows with Ubuntu VM (recommended)

Mininet and OVS need Linux networking features and elevated network namespace privileges. The VM workflow is the primary path; WSL is optional, and its networking/OVS support may vary.

1. In Windows, install VirtualBox or VMware, create an Ubuntu 22.04/24.04 VM (suggested: 4 vCPUs, 8 GB RAM, 25 GB disk), and install Ubuntu from its ISO. Use a host-only or bridged adapter so Windows can SSH to the guest.
2. In the Ubuntu VM, install SSH and find its address:

   ```bash
   sudo apt update && sudo apt install -y openssh-server
   hostname -I
   ```

3. In Windows PowerShell, install VS Code and the Remote - SSH extension, then copy the workspace to the VM. Replace `USER` and `VM_IP` with the Ubuntu account and address:

   ```powershell
   winget install --id Microsoft.VisualStudioCode -e
   code --install-extension ms-vscode-remote.remote-ssh
   scp -r "$env:USERPROFILE\OneDrive\Desktop\College\SDN\sdn_5g_network_slicing" USER@VM_IP:~/
   ```

4. In VS Code, connect to `USER@VM_IP` using **Remote - SSH**, then use **File → Open Folder** and open `~/sdn_5g_network_slicing`. Use the Ubuntu integrated terminal for Mininet commands. The project does not use xterm.

In Ubuntu, from the project root:

```bash
chmod +x scripts/*.sh
./scripts/install_ubuntu.sh
python3 -m venv .venv-ryu
source .venv-ryu/bin/activate
python -m pip install --upgrade pip
python -m pip install -c sdn_slicing/constraints-ryu.txt setuptools pbr wheel
python -m pip install --no-build-isolation -c sdn_slicing/constraints-ryu.txt -r sdn_slicing/requirements.txt
ryu-manager --version
```

### Why Ryu needs a pinned build environment

Ryu 4.34 is retained to avoid changing the controller API. Its source `setup.py` enables PBR, and its `ryu.hooks` setup hook relies on the legacy `setuptools.command.easy_install.get_script_args` API. Recent setuptools releases removed that API, producing the `easy_install.get_script_args` failure. Ryu's `setup.cfg` declares the `ryu` package through PBR's legacy `[files]` section; when PBR's configuration is not used in an isolated build, setuptools' flat-layout discovery sees both `etc` and `ryu` and raises the multiple top-level packages error. The install above pins setuptools/PBR and disables build isolation so that the declared PBR configuration is available to the build. The Ryu maintainers' issue tracker records the same `get_script_args` error and a successful setuptools 67.6.1 workaround. [Ryu 4.34 setup.py](https://github.com/faucetsdn/ryu/blob/v4.34/setup.py), [Ryu 4.34 setup.cfg](https://github.com/faucetsdn/ryu/blob/v4.34/setup.cfg), [Ryu issue #201](https://github.com/faucetsdn/ryu/issues/201).

Do not upgrade setuptools after this bootstrap in `.venv-ryu` without retesting Ryu. The project has not switched to OS-Ken: the build-tool workaround preserves the existing Ryu controller and launch command. If `ryu-manager --version` still fails after this procedure, retain the full traceback before changing controller frameworks.

For VS Code, install the Python and Remote - SSH extensions, connect to the Ubuntu VM, and use **File → Open Folder** to open the project directory. Run Mininet/OVS commands in the Ubuntu integrated terminal. Do not run them in ordinary Windows PowerShell.

## Run the controller and topology

Open two Ubuntu terminals at the project root.

Terminal 1:

```bash
source .venv-ryu/bin/activate
./scripts/start_controller.sh
```

Terminal 2:

```bash
sudo python3 sdn_slicing/topology.py
```

In the Mininet CLI, check reachability with `pingall`. The topology connects h1/h3/h5 to s1 and h2/h4/h6 to s2. The only inter-switch link is the 100 Mbps bottleneck. Queue setup is done after switches/ports exist:

```text
mininet> sh bash ./scripts/setup_qos.sh
```

If the interactive Mininet process was started with sudo, this shell runs as root. The standalone experiment runner below sets up queues itself.

## Run all three flows at once

For repeatable concurrent traffic and real result files, leave the controller running and run:

```bash
sudo python3 scripts/run_experiment.py 20
```

The runner starts the topology, configures OVS queues, starts three iperf3 servers and launches all three TCP clients before collecting results. It also runs a healthcare ping probe during the TCP load, then runs simultaneous UDP probes to collect direct loss and jitter fields. Each invocation creates timestamped `results/run_*.json` and `results/run_*.csv` from actual command output. No sample measurements are included. For manual TCP iperf3, start `iperf3 -s` on each even host, then run `iperf3 -c 10.0.0.2 -t 20`, `iperf3 -c 10.0.0.4 -t 20`, and `iperf3 -c 10.0.0.6 -t 20` concurrently from h1, h3 and h5 in the Mininet CLI.

To graph collected throughput after installing optional Matplotlib (`python3 -m pip install matplotlib`), run `python3 scripts/plot_results.py`. It reads only timestamped measurement CSVs.

## Inspect queue and flow configuration

From Ubuntu, while the topology is active:

```bash
sudo ovs-vsctl list Port s1-eth4
sudo ovs-vsctl list Port s2-eth4
sudo ovs-vsctl list QoS
sudo ovs-vsctl list Queue
sudo ovs-ofctl -O OpenFlow13 dump-flows s1
sudo ovs-ofctl -O OpenFlow13 dump-flows s2
sudo ovs-ofctl -O OpenFlow13 dump-queues s1 4
sudo ovs-ofctl -O OpenFlow13 dump-queues s2 4
```

Ports are created deterministically: each switch gets three host links first (ports 1–3), then trunk port 4. Confirm using `sudo ovs-ofctl -O OpenFlow13 show s1` and `show s2` if the topology code is changed.

## Tests

Run the local configuration/classifier/source/schema tests from Ubuntu or Windows Python:

```bash
python -m unittest discover -s tests -v
```

The static tests do not require Mininet or Ryu. Integration behavior requires a Linux host with Mininet, OVS and Ryu installed. Results should be interpreted against the configured minimum/maximum rates and repeated for stability; iperf TCP throughput can vary due to TCP startup, VM scheduling, CPU load and queue implementation.

## Troubleshooting

- **Controller not connected:** verify controller terminal is running, listener port 6653 is available, and switches target 127.0.0.1:6653.
- **No queue output:** run queue setup after Mininet creates the bridge ports, then check that `s1-eth4` and `s2-eth4` are the trunk egresses.
- **No iperf3:** install `iperf3` in Ubuntu and verify `iperf3 --version`; the server/client command comes from the Ubuntu package.
- **Permission errors:** run Mininet and its OVS commands with sudo. Do not reset global network configuration.
- **Ryu install errors:** use the pinned `setuptools==67.6.1` / `pbr==5.11.1` bootstrap above, then install with `--no-build-isolation`. Do not run an unconstrained setuptools upgrade in `.venv-ryu`.
- **Unreachable hosts:** inspect controller logs, `dump-flows`, `pingall`, and OpenFlow port numbering.

## Scope, limitations and future work

This fixed demonstration uses static host mappings, a single OpenFlow controller, three TCP service flows, proxy ARP, and Linux HTB queues. It has no production 5G core, radio access network, dynamic admission control, REST orchestration service, meter rules, NETCONF/P4Runtime, or real hospital traffic. The PDF mentions meters in its architecture; this implementation uses queue rate policies and explicitly does not claim meter enforcement. Future work could add a REST slice manager wired to flow updates, OpenFlow meters, dynamic topology discovery, UDP tests, graphing, failure recovery, and repeatable multi-run statistical analysis.

Safe cleanup after stopping Mininet:

```bash
./scripts/cleanup.sh
```

## Assignment answers

**i. SDN and slicing.** SDN separates the decision logic from packet forwarding. The slice manager expresses each service's bandwidth and latency intent; the controller maps each host flow to an explicit path and queue. Thus broadband, healthcare and sensor traffic share the same switches and trunk while receiving distinct queue treatment and flow-level separation.

**ii. Slice design.** The configurable proposal is 50–80 Mbps broadband, 20–30 Mbps healthcare and 10–20 Mbps IoT, with best-effort, 10 ms and 100 ms latency objectives respectively. Only the differentiation requirement comes from the assignment; those numbers are lab assumptions. The controller matches IPv4 source/destination pairs, chooses a queue for trunk egress, and installs delivery flows in both directions. OVS HTB applies min/max rates; separate queues isolate scheduling and caps. Monitoring uses iperf throughput, ping round-trip time, and OVS flow/queue inspection. Actual latency also depends on propagation, host/VM scheduling, TCP, switch behavior and load.

**iii. Congestion.** Healthcare should receive preferential scheduling and its configured minimum where HTB can honor it. Broadband may fall below its peak but should stay within its cap and receive available capacity. IoT should retain its configured share where feasible and not be indefinitely starved. These are intended policies to verify experimentally: queue priority alone does not create a hard end-to-end latency guarantee.
