# Experimental plan

## Objective

Show three TCP service pairs sharing one 100 Mbps link, with queue and flow configuration that reflects the configured policies. Test nominal simultaneous load and congestion by selecting a duration and/or increasing offered load in later extensions.

## Variables and metrics

- Independent: per-slice minimum and maximum rate; offered TCP load; link capacity; repeat number.
- Dependent: TCP iperf3 receiver throughput and retransmits per slice; UDP iperf3 loss percentage and jitter; healthcare ping minimum/average/maximum RTT; observed OVS queue and OpenFlow configuration.
- Controlled: fixed topology, host addresses, controller version, run duration and VM allocation.

Initial config rates and latency objectives are proposed lab values, not values mandated by the PDF. The bundled runner uses one TCP client per pair concurrently. To test saturation clearly, the runner can be extended with parallel streams (`iperf3 -P`) or longer durations; record any changed offered-load settings alongside the result.

## Procedure

1. Start Ryu controller and confirm both switches connect.
2. Run the experiment script with a per-phase duration, e.g. `sudo python3 scripts/run_experiment.py 30`. It runs one concurrent TCP phase, a concurrent UDP probe phase, and a healthcare ping probe during TCP traffic.
3. Confirm that three clients overlapped and inspect their receiver rates in the printed report.
4. Inspect `s1`/`s2` flows and queue assignments with the README commands.
5. Repeat at least three times for a report and compare rate ranges and RTT variation.
6. Keep every timestamped result file and record any deviation from config.

## Interpretation

Compare measured receiver rate with configured minimum and cap. A configured HTB minimum is a scheduling parameter; measured TCP throughput can be lower due to startup, path/host limitations or scheduler behavior. Compare ping RTT under simultaneous traffic to the proposed healthcare objective, but do not call it guaranteed latency. Compare queue/flow tables to demonstrate classification and enforcement intent. Congestion analysis should report when broadband yields capacity, whether healthcare retains priority, and whether IoT retains service. Do not fabricate missing measurements.
