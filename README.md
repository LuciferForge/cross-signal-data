# cross-signal-data

**The labeled Polymarket crash-recovery dataset behind a 79.8% win-rate live trading bot.**

308 closed trades. Real Polymarket markets. Real entry triggers. Real outcomes. Public for anyone who wants to build their own mean-reversion bot, replicate our results, or prove us wrong.

## What's in here

A single CSV (`data/crashes_v1.csv`) with one row per closed trade on Polymarket where the [crash-recovery bot](https://github.com/LuciferForge/polymarket-crash-bot) entered. Each row has:

- The market (public Polymarket `market_id` and question text)
- The signal (`pre_crash_high`, `entry_price`, `drop_pct`)
- The outcome (`exit_price`, `exit_reason`, `pnl_usd`, `is_profitable`)
- Time features (`entry_hour_utc`, `entry_dow`, `hold_hours`)

| Stat | Value |
|------|-------|
| Total trades | 308 |
| Profitable | 247 (80.2%) |
| Date range | March 2026 – April 2026 |
| Median hold | ~3 hours |
| Avg drop_pct at entry | ~22% |
| Avg recovered_to_pct_of_high | ~85% |

| Exit reason | Count |
|-------------|-------|
| RECOVERY (price came back) | 235 |
| TIMEOUT_48H (held 48h, exited) | 62 |
| TIMEOUT (early TIMEOUT exit) | 11 |

## Why this exists

Most prediction-market datasets are either:
- **Synthetic** (generated for academic papers, no real money behind them), or
- **Aggregate** (volume, liquidity at hourly resolution — useless for tactical signals)

This is neither. It's the actual labeled examples of a single specific signal — *Polymarket markets that crashed N% from a recent high* — paired with the actual outcome of trading the recovery. If you want to study whether mean-reversion works on prediction markets, this is the data.

## Install

```bash
pip install cross-signal-data
```

## Quick use (Python)

```python
from cross_signal_data import load

df = load()
print(df.shape)              # (308, 19)
print(df.columns.tolist())   # full list of fields

# Filter to RECOVERY-only trades
recovered = df[df["exit_reason"] == "RECOVERY"]

# What entry-price bucket has the best win rate?
buckets = df.groupby(df["entry_price"].round(2)).agg(
    n=("trade_id", "count"),
    win_rate=("is_profitable", "mean"),
)
print(buckets)
```

If you don't have pandas:

```python
from cross_signal_data import load
rows = load(as_pandas=False)  # list of dicts
print(len(rows), rows[0])
```

## Quick use (any language)

The file is plain CSV. Just download it:

```bash
curl -o crashes_v1.csv https://raw.githubusercontent.com/LuciferForge/cross-signal-data/main/data/crashes_v1.csv
```

## Schema

See [`docs/schema.md`](docs/schema.md) for full column-by-column documentation.

Key columns:
- `entry_price` — the price-per-share when the bot entered (0–1)
- `pre_crash_high` — the recent local-window high
- `drop_pct` — `(pre_crash_high − entry_price) / pre_crash_high × 100`
- `exit_reason` — `RECOVERY`, `TIMEOUT_48H`, `TIMEOUT`, or `STOP`
- `is_profitable` — 1 if `pnl_usd > 0` else 0
- `recovered_to_pct_of_high` — `exit_price / pre_crash_high × 100`

## Methodology

See [`docs/methodology.md`](docs/methodology.md) for:
- How the crash signal is defined
- Entry/exit rules
- Known biases (survivorship: only triggers that fired are recorded; a different threshold might surface different examples)
- What's NOT in the data (slippage cost — see [pnl-truthteller](https://github.com/LuciferForge/pnl-truthteller) for the slippage layer)

## Reproducibility

The script that generated this dataset is in [`scripts/extract.py`](scripts/extract.py). Anyone with the source `positions.json` from the bot can rerun it:

```bash
python scripts/extract.py \
    --positions /path/to/positions.json \
    --output data/crashes_v1.csv
```

## Baseline notebook

[`notebooks/baseline_model.py`](notebooks/baseline_model.py) trains a logistic regression and random forest on the dataset to predict `is_profitable`.

Result: **~79.9% cross-validated accuracy** with simple features — essentially matching the bot's 80.2% WR. Translation: most of the alpha is **in the entry trigger itself** (which already filters to high-WR setups), not in further feature engineering. If you want to beat this dataset, you almost certainly need features the bot doesn't currently log (orderbook depth, market category, time-to-resolution).

Top feature importances from the random forest:

| Feature | Importance |
|---------|-----------:|
| `drop_pct` | 0.254 |
| `shares` | 0.200 |
| `entry_price` | 0.174 |
| `pre_crash_high` | 0.171 |
| `entry_hour_utc` | 0.110 |
| `entry_dow` | 0.059 |

A clean, exploitable insight from the diurnal column: win rate at hours 16, 21, 22 UTC reaches ~100% (small samples though); hour 8 UTC dips to ~55%. Off-peak hours are punishing. Adjust your live-firing schedule accordingly.

```bash
pip install cross-signal-data[ml]
python notebooks/baseline_model.py
```

## Versioning

| Version | Date | Trades | Notes |
|---------|------|--------|-------|
| v1 | 2026-04-28 | 308 | Initial public release |

Future versions will add more trades, more features (orderbook depth at entry, market category, time-to-resolution) and possibly per-market metadata. Pin to a specific version if reproducibility matters: `load(version="v1")`.

## License

**Code: MIT.** Use the loader, the extraction script, and the baseline notebook however you want.

**Data: MIT.** Public on-chain prediction market data, transformed into a labeled dataset. Cite if you use it in research.

## Citation

```bibtex
@dataset{cross_signal_data_2026,
    title  = {cross-signal-data: Polymarket crash-recovery labeled dataset},
    author = {LuciferForge},
    year   = {2026},
    url    = {https://github.com/LuciferForge/cross-signal-data}
}
```

## About the author

Built by [LuciferForge](https://github.com/LuciferForge), running a [public-audited Polymarket crash bot](https://github.com/LuciferForge/polymarket-crash-bot) (308 closed trades, 80.2% WR, all data here). Also runs:
- [polymarket-mcp](https://github.com/LuciferForge/polymarket-mcp) — MCP server for live Polymarket data
- [pnl-truthteller](https://github.com/LuciferForge/pnl-truthteller) — slippage audit tool
- [polymarket-v2-migration](https://github.com/LuciferForge/polymarket-v2-migration) — V1→V2 cookbook
- [protodex.io](https://protodex.io) — public MCP-server index
