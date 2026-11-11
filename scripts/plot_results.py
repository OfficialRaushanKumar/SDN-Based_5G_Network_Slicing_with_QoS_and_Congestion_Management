#!/usr/bin/env python3
"""Plot throughput from real timestamped experiment CSV files."""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = sorted((ROOT / "results").glob("run_*.csv"))
if not files:
    raise SystemExit("No run_*.csv measurements found in results/. Run an experiment first.")
try:
    import matplotlib.pyplot as plt
except ImportError as exc:
    raise SystemExit("Install optional plotting dependency with: python3 -m pip install matplotlib") from exc

labels, values = [], []
for path in files:
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            labels.append(f'{path.stem.removeprefix("run_")}\n{row["slice"]}')
            values.append(float(row["throughput_mbps"]))
if not labels:
    raise SystemExit("Result CSV files contained no measurements.")
plt.figure(figsize=(max(9, len(labels) * 1.1), 5))
plt.bar(labels, values, color=[{"broadband": "#4472c4", "healthcare": "#c0504d", "iot": "#70ad47"}.get(label.split("\n")[-1], "#888888") for label in labels])
plt.ylabel("Measured receiver throughput (Mbps)")
plt.xlabel("Actual run and slice")
plt.title("SDN slicing experiment: measured throughput")
plt.xticks(rotation=35, ha="right")
plt.tight_layout()
output = ROOT / "results" / "throughput_comparison.png"
plt.savefig(output, dpi=160)
print(f"Saved plot from measured CSV data: {output}")
