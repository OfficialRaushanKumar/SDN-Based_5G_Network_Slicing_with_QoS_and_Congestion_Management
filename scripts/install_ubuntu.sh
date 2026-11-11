#!/usr/bin/env bash
set -euo pipefail
sudo apt update
sudo apt install -y mininet openvswitch-switch iperf3 python3 python3-pip python3-venv git iproute2
echo "Create the Ryu environment separately using docs/implementation.md (Python 3.10/3.11 recommended)."
