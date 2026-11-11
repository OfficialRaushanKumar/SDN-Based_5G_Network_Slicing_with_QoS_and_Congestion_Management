#!/usr/bin/env bash
set -euo pipefail
sudo mn -c
for port in s1-eth4 s2-eth4; do
  if sudo ovs-vsctl --if-exists get Port "$port" name >/dev/null 2>&1; then
    sudo ovs-vsctl clear Port "$port" qos
  fi
done
echo "Mininet state cleaned; any remaining OVS bridge configuration was left intact."
