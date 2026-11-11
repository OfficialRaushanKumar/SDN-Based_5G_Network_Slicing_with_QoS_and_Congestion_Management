#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CFG="$ROOT/config/slices.json"
declare -a QUEUES MINS MAXES PRIORITIES
while IFS=, read -r queue minimum maximum priority; do
  QUEUES+=("$queue"); MINS+=("$minimum"); MAXES+=("$maximum"); PRIORITIES+=("$priority")
done < <(python3 - "$CFG" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as stream:
    cfg = json.load(stream)
for s in cfg["slices"]:
    print(f'{s["queue_id"]},{int(s["min_mbps"]*1_000_000)},{int(s["max_mbps"]*1_000_000)},{s["priority"]}')
PY
)

for port in s1-eth4 s2-eth4; do
  args=(--)
  queue_map=()
  for index in "${!QUEUES[@]}"; do
    queue="${QUEUES[$index]}"
    args+=(--id="@q${queue}" create Queue "other-config:min-rate=${MINS[$index]}" "other-config:max-rate=${MAXES[$index]}" "other-config:priority=${PRIORITIES[$index]}")
    queue_map+=("queues:${queue}=@q${queue}")
  done
  args+=(-- --id=@qos create QoS type=linux-htb other-config:max-rate=100000000 "${queue_map[@]}" -- set Port "$port" qos=@qos)
  ovs-vsctl "${args[@]}"
done
echo "Configured all per-slice HTB queues on both shared-link egress ports."
