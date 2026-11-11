#!/usr/bin/env python3
"""Print validated slice requirements from config/slices.json."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sdn_slicing.config import load_config

cfg = load_config()
print(f'Shared link: {cfg["link"]["capacity_mbps"]} Mbps')
for item in cfg["slices"]:
    latency = item.get("latency_objective_ms")
    print(f'{item["id"]}: {item["service"]}; {item["src_host"]}<->{item["dst_host"]}; queue={item["queue_id"]}; '
          f'min/max={item["min_mbps"]}/{item["max_mbps"]} Mbps; latency objective={latency if latency is not None else "best effort"}; '
          f'priority={item["priority"]}; isolation={item["isolation"]}')
