# Viva questions and answers

1. **What is SDN?** Software Defined Networking separates control decisions from packet forwarding so control software can program network devices.
2. **What is network slicing?** It is the logical partitioning of shared infrastructure into service-specific policies and resources.
3. **Why use slices here?** Broadband, remote surgery and sensors have different throughput and delay needs even though they share a transport link.
4. **What is the application plane?** It expresses service intent; this project stores that intent in `config/slices.json`.
5. **What is the control plane?** It decides paths and actions; Ryu installs the demo's OpenFlow rules.
6. **What is the data plane?** It forwards packets and applies queue scheduling; here it is Open vSwitch.
7. **What does OpenFlow do?** It lets a controller install match/action forwarding entries on a switch.
8. **Which OpenFlow version is used?** OpenFlow 1.3, selected by the Ryu app and the OVS switches.
9. **What is Ryu?** A Python SDN controller framework that handles switch events and programs flow tables.
10. **What is Mininet?** A Linux network emulator that creates virtual hosts, links and switches for experiments.
11. **What is OVS?** Open vSwitch is a software switch with programmable flow tables and QoS support.
12. **What is QoS?** Quality of Service policies differentiate traffic using measures such as rate, priority, loss and delay.
13. **What is HTB?** Hierarchical Token Bucket is a Linux traffic control scheduler that shapes classes with rate and ceiling settings.
14. **How is a flow mapped to a queue?** The controller matches configured IPv4 endpoint pairs and applies an OpenFlow set-queue action before trunk output.
15. **Why configure queues on both switches?** The shared trunk carries traffic in both directions, so each egress needs matching queue configuration.
16. **What is a minimum rate?** It is a scheduler allocation target under contention when resources and implementation permit it; it is not an unconditional physical guarantee.
17. **What is a maximum rate?** It caps the rate that a queue can consume.
18. **Does queue priority guarantee latency?** No. Propagation, packet serialization, queue depth, host scheduling and the rest of the path also affect latency.
19. **What is latency?** Time for a packet or message to travel from source to destination; ping reports round-trip time.
20. **What is jitter?** Variation in packet delay over time.
21. **What is packet loss?** Packets that fail to reach their destination; this TCP demo records retransmits, which are not the same as a direct loss percentage.
22. **How should congestion affect healthcare?** Give it the intended higher scheduling treatment and configured minimum, then measure throughput and RTT under load.
23. **How should congestion affect broadband?** Its throughput may fall below peak when other protected queues need capacity; its maximum remains a cap.
24. **How should congestion affect IoT?** Preserve its configured allocation where possible so many low-rate flows are not starved.
25. **What isolation does this demo provide?** Separate flow matches and HTB queues with caps; it does not provide cryptographic or production tenant isolation.
26. **What does iperf3 measure?** It generates traffic and reports throughput and other transport statistics between endpoints.
27. **Why run clients concurrently?** This makes all service classes contend for the same bottleneck at the same time.
28. **What is the role of proxy ARP?** It answers host address-resolution requests for the fixed endpoints so traffic can follow the controller's explicit IPv4 forwarding rules.
29. **Does the project implement NETCONF or P4Runtime?** No. Those are alternatives named in the assignment; the implemented southbound protocol is OpenFlow 1.3.
30. **Does the project implement a full 5G system?** No. It demonstrates transport slicing concepts in Mininet/OVS and does not include a 5G core or radio network.
31. **How do you verify queue mapping?** Inspect OpenFlow entries with `ovs-ofctl dump-flows` and queue records/counters with `ovs-vsctl` and `ovs-ofctl dump-queues`.
32. **Why repeat experiments?** TCP startup, VM scheduling and host load vary; repeated measurements make conclusions more reliable.
33. **What is a limitation of static flow rules?** They are tied to the fixed host addresses and topology and do not adapt to arbitrary host changes.
34. **What is the difference between a queue and a meter?** A queue schedules packets at an egress; a meter measures or rate-limits matched flows. This demo uses queues and does not install meters.
