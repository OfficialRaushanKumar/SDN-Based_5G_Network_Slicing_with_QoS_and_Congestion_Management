"""Load and validate the central slice configuration."""
import json
from pathlib import Path


def load_config(path=None):
    config_path = Path(path) if path else Path(__file__).resolve().parents[1] / "config" / "slices.json"
    with config_path.open(encoding="utf-8") as stream:
        config = json.load(stream)
    validate_config(config)
    return config


def validate_config(config):
    link = config.get("link", {})
    capacity = link.get("capacity_mbps")
    slices = config.get("slices")
    if not isinstance(capacity, (int, float)) or capacity <= 0:
        raise ValueError("link.capacity_mbps must be positive")
    if not isinstance(slices, list) or len(slices) != 3:
        raise ValueError("exactly three slices are required")
    ids, queues, hosts = set(), set(), set()
    minimum_total = 0
    for item in slices:
        for field in ("id", "service", "src_host", "dst_host", "queue_id", "min_mbps", "max_mbps", "priority", "protocol", "isolation"):
            if field not in item:
                raise ValueError(f"slice missing required field: {field}")
        if item["id"] in ids or item["queue_id"] in queues:
            raise ValueError("slice IDs and queue IDs must be unique")
        ids.add(item["id"]); queues.add(item["queue_id"])
        if item["src_host"] == item["dst_host"] or item["src_host"] in hosts or item["dst_host"] in hosts:
            raise ValueError("each slice must use a distinct communicating host pair")
        hosts.update((item["src_host"], item["dst_host"]))
        if not (0 < item["min_mbps"] <= item["max_mbps"] <= capacity):
            raise ValueError(f"invalid rates for slice {item['id']}")
        if item["queue_id"] < 0 or item["priority"] < 1:
            raise ValueError(f"invalid queue or priority for slice {item['id']}")
        minimum_total += item["min_mbps"]
    if minimum_total > capacity:
        raise ValueError("sum of minimum rates exceeds shared link capacity")
    if len(hosts) != 6:
        raise ValueError("the demo requires six distinct hosts")
    return True
