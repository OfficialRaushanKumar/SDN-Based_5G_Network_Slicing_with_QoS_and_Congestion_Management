# Results analysis template

Use actual files in `results/`; leave unknown values blank. Never infer a measured result from queue configuration alone.

## Run metadata

- Run ID / UTC timestamp:
- Ubuntu, kernel, Mininet, OVS, Ryu and iperf3 versions:
- VM CPU / memory:
- Config revision and duration:
- Any failed host, client or controller:

## Measurements

| Slice | Queue | Configured min/max Mbps | TCP receiver Mbps | TCP retransmits | UDP loss % | UDP jitter ms | Meets min? |
|---|---:|---:|---:|---:|---:|---:|---|
| Broadband | 0 | 50 / 80 | | | | | |
| Healthcare | 1 | 20 / 30 | | | | | |
| IoT | 2 | 10 / 20 | | | | | |

- Healthcare ping RTT min/avg/max (ms):
- Sum of measured throughput (Mbps):
- Flow table confirms intended queue actions? 
- OVS queue table confirms min/max values?

## Discussion

Describe how simultaneous traffic competed for the 100 Mbps trunk. Compare measurements with the configured rates and explain any shortfall. Discuss healthcare delay against the proposed objective and state that queue priority does not alone guarantee end-to-end latency. Explain whether IoT retained service and whether broadband yielded peak rate. Include run-to-run variation and limitations; do not present a single VM run as a production SLA.
