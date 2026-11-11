#!/usr/bin/env python3
"""Run three simultaneous iperf3 flows, a healthcare ping probe, and save real results."""
import csv
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sdn_slicing"))
from topology import SlicingTopo
from config import load_config
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.link import TCLink


def main():
    cfg = load_config()
    topo = SlicingTopo(capacity=cfg["link"]["capacity_mbps"], delay=f'{cfg["link"]["delay_ms"]}ms')
    net = Mininet(topo=topo, controller=None, switch=OVSSwitch, link=TCLink, autoSetMacs=True, build=True)
    net.addController("c0", controller=RemoteController, ip="127.0.0.1", port=6653)
    net.start()
    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    try:
        time.sleep(2)
        subprocess.run(["bash", str(ROOT / "scripts" / "setup_qos.sh")], check=True)
        host_by_name = {h.name: h for h in net.hosts}
        servers = [host_by_name[s["dst_host"]].popen(["iperf3", "-s"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for s in cfg["slices"]]
        time.sleep(1)
        duration = int(sys.argv[1]) if len(sys.argv) > 1 else 20
        clients = {}
        for s in cfg["slices"]:
            src = host_by_name[s["src_host"]]
            clients[s["id"]] = src.popen(["iperf3", "-c", f'10.0.0.{int(s["dst_host"][1:])}', "-t", str(duration), "-J"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        ping = host_by_name["h3"].popen(["ping", "-c", str(max(5, duration)), "-i", "1", "10.0.0.4"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        records = []
        for s in cfg["slices"]:
            process = clients[s["id"]]
            stdout, stderr = process.communicate(timeout=duration + 30)
            if process.returncode:
                raise RuntimeError(f'iperf3 failed for {s["id"]}: {stderr.strip()}')
            report = json.loads(stdout)
            summary = report.get("end", {}).get("sum_received", report.get("end", {}).get("sum", {}))
            sent = report.get("end", {}).get("sum_sent", {})
            records.append({"timestamp_utc": datetime.now(timezone.utc).isoformat(), "slice": s["id"], "queue_id": s["queue_id"], "min_mbps": s["min_mbps"], "max_mbps": s["max_mbps"], "throughput_mbps": summary.get("bits_per_second", 0) / 1e6, "sender_retransmits": sent.get("retransmits"), "duration_s": duration})
        # A second concurrent UDP probe phase provides direct loss/jitter fields from iperf3.
        udp_clients = {}
        for s in cfg["slices"]:
            src = host_by_name[s["src_host"]]
            bitrate = max(1, int(s["min_mbps"] / 10))
            udp_clients[s["id"]] = src.popen(["iperf3", "-c", f'10.0.0.{int(s["dst_host"][1:])}', "-u", "-b", f"{bitrate}M", "-t", str(duration), "-J"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for record in records:
            process = udp_clients[record["slice"]]
            stdout, stderr = process.communicate(timeout=duration + 30)
            if process.returncode:
                raise RuntimeError(f'iperf3 UDP probe failed for {record["slice"]}: {stderr.strip()}')
            udp_report = json.loads(stdout)
            udp_sum = udp_report.get("end", {}).get("sum_received", udp_report.get("end", {}).get("sum", {}))
            record["udp_probe_mbps"] = max(1, int(record["min_mbps"] / 10))
            record["udp_loss_percent"] = udp_sum.get("lost_percent")
            record["udp_jitter_ms"] = udp_sum.get("jitter_ms")
        ping_out, _ = ping.communicate(timeout=duration + 10)
        match = re.search(r"rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)", ping_out)
        latency = {"healthcare_ping_avg_ms": float(match.group(2)) if match else None, "healthcare_ping_min_ms": float(match.group(1)) if match else None, "healthcare_ping_max_ms": float(match.group(3)) if match else None}
        data = {"run_id": stamp, "timestamp_utc": datetime.now(timezone.utc).isoformat(), "bottleneck_mbps": cfg["link"]["capacity_mbps"], "duration_s": duration, "measurements": records, "latency": latency, "note": "Measured values from this run; not guaranteed outcomes."}
        json_path = results_dir / f"run_{stamp}.json"
        json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        csv_path = results_dir / f"run_{stamp}.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0]))
            writer.writeheader(); writer.writerows(records)
        print(json.dumps(data, indent=2))
    finally:
        for proc in locals().get("servers", []):
            proc.terminate()
        net.stop()


if __name__ == "__main__":
    main()
