# Methodology

How the dataset was generated and what biases you should know about.

## The signal

The crash-recovery bot enters when, **on a Polymarket binary or multi-outcome market**:

1. The price has dropped > **N%** from a recent local-window high (`pre_crash_high`).
2. The current `entry_price` is in a sweet-spot range (default: $0.04 – $0.30 in earlier versions; raised to $0.04 – $0.60 in the current version).
3. The market is not in a per-token loss cooldown (post-TIMEOUT 7d block).
4. Market category is not in the persistent blacklist (sports markets where the team has lost the underlying game, etc.).
5. The orderbook has enough depth at the bid stack to absorb the position size within the slippage budget.

When all conditions hit, the bot opens a position with `size_usd = 5` (standard size in this dataset).

## The exits

The bot closes a position when one of:

- **`RECOVERY`** — `exit_price` reaches a target % of `pre_crash_high` (default: 90% of pre-crash). Most common path. Profitable.
- **`TIMEOUT_48H`** — held for 48 hours without recovering. Bot exits at whatever the bid stack offers. Sometimes profitable (drift), often a small loss.
- **`TIMEOUT`** — older shorter-window timeout variant from earlier in the dataset. Same logic, shorter window.
- **`STOP`** — price keeps dropping below a stop level. Rare in this dataset because the bot's stop is loose (the thesis is "crashes mean-revert," so giving the position room is intentional).

## Known biases

### 1. Survivorship in the trigger

This dataset only contains markets where the trigger fired. If you'd used a different threshold (say, 25% drop instead of the bot's default 20%), you'd see different markets. The data does NOT generalize to "all Polymarket crashes" — it generalizes to "Polymarket crashes that fit this specific signal profile."

### 2. Selection in the entry-price band

The bot only enters when `entry_price` is in the configured range. If a market crashes from $0.80 → $0.50, the bot ignores it (above the range). If a market is at $0.02, the bot ignores it (below the floor). The dataset is therefore **heavy in the $0.04–$0.30 band**.

### 3. Theoretical PnL ≠ realized PnL

`pnl_usd` and `is_profitable` are computed from `entry_price` and `exit_price` — what the bot's order tickets said. Actual on-chain fills typically come in slightly worse, especially for `TIMEOUT_48H` exits where the book is thin. See [pnl-truthteller](https://github.com/LuciferForge/pnl-truthteller) for slippage-adjusted analysis.

### 4. Time period

Data covers **March–April 2026**. This includes:
- A Polymarket V2 migration period (April 28 cutover) where bot was paused for ~6 hours
- Various political and sports events specific to that window
- Polygon network conditions specific to that period (gas costs, liquidity)

Don't assume the patterns extrapolate forward indefinitely. Re-run extraction quarterly as the dataset grows.

### 5. One bot, one strategy, one operator

This is data from a single bot run by a single operator. It is **not** a representative sample of all Polymarket activity, all mean-reversion strategies, or all market participants. Treat it as a case study of one specific strategy executed live.

## What's NOT in the data

- **Order-book depth at entry** — would need historical orderbook snapshots, not currently logged.
- **Market category** — currently must be looked up via the Polymarket gamma-api using `market_id`.
- **Time-to-resolution at entry** — same; available via gamma-api.
- **Other concurrent positions** — capital allocation may have constrained which trades fired.
- **Slippage** — separate tool: [pnl-truthteller](https://github.com/LuciferForge/pnl-truthteller).

## What kind of analysis this dataset is good for

- **Mean-reversion alpha studies** — does crash-recovery actually work? At what drop_pct does it start working? The data has all the inputs.
- **Time-of-day effects** — `entry_hour_utc` × `is_profitable` reveals the diurnal pattern.
- **Hold-time tradeoffs** — the win-rate vs hold-hours curve is in here.
- **Feature-engineering exercises** — if you can predict `is_profitable` better than 80% accuracy from these features, you've found something.
- **Backtesting frameworks** — this is real labeled data with real prices, suitable for cross-validation.

## What kind of analysis this dataset is NOT good for

- **General Polymarket research** — too narrow a slice (one bot, one signal).
- **High-frequency studies** — only entry/exit timestamps, not tick-level data.
- **Slippage modeling** — see [pnl-truthteller](https://github.com/LuciferForge/pnl-truthteller).
- **Counterfactuals** ("what would a different bot have done?") — only triggered trades are recorded.
