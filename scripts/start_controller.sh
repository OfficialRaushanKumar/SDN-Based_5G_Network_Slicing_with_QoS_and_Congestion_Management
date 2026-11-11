#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RYU_BIN="${RYU_BIN:-$ROOT/.venv-ryu/bin/ryu-manager}"
if [[ ! -x "$RYU_BIN" ]]; then
  echo "Ryu executable not found at $RYU_BIN; see README setup instructions." >&2
  exit 1
fi
cd "$ROOT"
exec "$RYU_BIN" --ofp-tcp-listen-port 6653 sdn_slicing/controller.py
