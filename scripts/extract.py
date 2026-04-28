#!/usr/bin/env python3
"""Extract closed-trade dataset from the LuciferForge crash bot's positions.json.

This is the script that generated `data/crashes_v1.csv`. It's checked in for
reproducibility — anyone with the source positions.json can rerun and get the
same output.

Usage:
    python scripts/extract.py \\
        --positions ~/Documents/LuciferForge/agents/trader/crash_monitor_data/positions.json \\
        --output data/crashes_v1.csv

The output is purely public data: Polymarket market IDs, prices, timestamps,
exit reasons. No private state (wallet addresses, private keys, API keys).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path


COLUMNS = [
    "trade_id",
    "market_id",
    "question",
    "outcome_label",
    "entry_time",
    "exit_time",
    "entry_price",
    "exit_price",
    "pre_crash_high",
    "drop_pct",
    "size_usd",
    "shares",
    "hold_hours",
    "pnl_usd",
    "is_profitable",
    "exit_reason",
    "entry_hour_utc",
    "entry_dow",  # 0=Mon, 6=Sun
    "recovered_to_pct_of_high",
]


def _safe_float(x, default=0.0):
    try:
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return default
        return v
    except (TypeError, ValueError):
        return default


def _parse_iso_utc(s: str | None):
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def transform_row(row: dict, idx: int) -> dict | None:
    """Turn a raw positions.json `closed` row into a dataset row."""
    entry_dt = _parse_iso_utc(row.get("entry_time"))
    if entry_dt is None:
        return None

    entry_price = _safe_float(row.get("entry_price"))
    exit_price = _safe_float(row.get("exit_price"))
    pre_high = _safe_float(row.get("pre_crash_high"))
    pnl = _safe_float(row.get("pnl"))

    drop_pct = 0.0
    if pre_high > 0 and entry_price > 0:
        drop_pct = (pre_high - entry_price) / pre_high * 100.0

    recovered_pct = 0.0
    if pre_high > 0 and exit_price > 0:
        recovered_pct = exit_price / pre_high * 100.0

    return {
        "trade_id": idx,
        "market_id": str(row.get("market_id") or ""),
        "question": (row.get("question") or "").replace("\n", " ").replace("\r", " "),
        "outcome_label": str(row.get("outcome_label") or ""),
        "entry_time": entry_dt.isoformat(timespec="seconds"),
        "exit_time": row.get("exit_time") or "",
        "entry_price": round(entry_price, 6),
        "exit_price": round(exit_price, 6),
        "pre_crash_high": round(pre_high, 6),
        "drop_pct": round(drop_pct, 4),
        "size_usd": round(_safe_float(row.get("size_usd")), 4),
        "shares": round(_safe_float(row.get("shares")), 4),
        "hold_hours": round(_safe_float(row.get("hold_hours")), 4),
        "pnl_usd": round(pnl, 4),
        "is_profitable": int(pnl > 0),
        "exit_reason": str(row.get("exit_reason") or ""),
        "entry_hour_utc": entry_dt.hour,
        "entry_dow": entry_dt.weekday(),
        "recovered_to_pct_of_high": round(recovered_pct, 4),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--positions", required=True, help="Path to positions.json")
    p.add_argument("--output", default="data/crashes_v1.csv", help="Output CSV path")
    args = p.parse_args()

    pos_path = Path(args.positions)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    data = json.loads(pos_path.read_text())
    closed = data.get("closed", []) if isinstance(data, dict) else []

    rows: list[dict] = []
    for i, raw in enumerate(closed):
        r = transform_row(raw, i)
        if r is not None:
            rows.append(r)

    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # Summary
    n = len(rows)
    n_profit = sum(r["is_profitable"] for r in rows)
    by_reason: dict[str, int] = {}
    for r in rows:
        by_reason[r["exit_reason"]] = by_reason.get(r["exit_reason"], 0) + 1

    print(f"Extracted {n} closed trades → {out_path}")
    print(f"Profitable: {n_profit} / {n} ({n_profit/n*100:.1f}%)")
    print("By exit reason:")
    for reason, count in sorted(by_reason.items(), key=lambda x: -x[1]):
        print(f"  {reason:20} {count:4}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
