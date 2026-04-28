# Schema — `crashes_v1.csv`

19 columns, one row per closed Polymarket trade.

| Column | Type | Description |
|--------|------|-------------|
| `trade_id` | int | Sequential 0-indexed trade ID for cross-referencing with the bot's own logs. |
| `market_id` | str | Polymarket market ID. Public — queryable via `gamma-api.polymarket.com/markets?id=<market_id>`. |
| `question` | str | The market question text at the time of the trade. |
| `outcome_label` | str | The YES/NO outcome the bot bet on. Most rows are `Yes` (the bot bets on the high-probability side). |
| `entry_time` | str (ISO-8601 UTC) | When the crash trigger fired and the bot opened the position. |
| `exit_time` | str (ISO-8601 UTC) | When the position closed (sell completed). |
| `entry_price` | float (0–1) | Per-share price at entry. Polymarket prices are probabilities. |
| `exit_price` | float (0–1) | Per-share price at exit. |
| `pre_crash_high` | float (0–1) | The recent local-window high used as the crash reference. The signal fires when current price drops > X% from this high. |
| `drop_pct` | float | `(pre_crash_high − entry_price) / pre_crash_high × 100`. Magnitude of the crash. |
| `size_usd` | float | USD allocated to the trade (typically $5 in this dataset). |
| `shares` | float | Share count purchased = `size_usd / entry_price`. |
| `hold_hours` | float | Wall-clock hours from `entry_time` to `exit_time`. |
| `pnl_usd` | float | Realized P&L in USD. **Theoretical, not slippage-adjusted.** Use [pnl-truthteller](https://github.com/LuciferForge/pnl-truthteller) for slippage-adjusted PnL. |
| `is_profitable` | int (0/1) | 1 if `pnl_usd > 0`, 0 otherwise. The default classification target. |
| `exit_reason` | str | `RECOVERY` (price came back), `TIMEOUT_48H` (held 48h, exited at whatever price), `TIMEOUT` (older shorter-timeout variant), or `STOP` (hit stop-loss — rare). |
| `entry_hour_utc` | int (0–23) | Hour-of-day at entry, UTC. |
| `entry_dow` | int (0–6) | Day-of-week at entry. 0 = Monday, 6 = Sunday. |
| `recovered_to_pct_of_high` | float | `exit_price / pre_crash_high × 100`. How close to the pre-crash high did the price come back. |

## Notes on usage

### `pnl_usd` is theoretical, not slippage-adjusted

The bot's internal records compute `pnl = (exit_price - entry_price) × shares`. This assumes you got every share filled at the listed entry/exit prices. In practice on thin Polymarket books, fills are noisier — the actual on-chain proceeds are typically lower than theoretical. See the methodology doc for context.

If you need slippage-adjusted P&L, the [pnl-truthteller](https://github.com/LuciferForge/pnl-truthteller) tool reconciles bot records against on-chain fills. The aggregate slippage on this dataset is roughly **-$120 across 300+ trades**, so the bot's lifetime claim of "+$33 theoretical" becomes "-$90 actual" once slippage is included.

### `RECOVERY` vs `TIMEOUT_48H`

If you're modeling for a binary classifier:
- Use `is_profitable` (clean 0/1) — most uses.
- If you want a 4-class outcome label, use `exit_reason` directly.

### `entry_dow` and `entry_hour_utc`

Trade timing has measurable signal. Markets are thinner overnight UTC (NA/Europe asleep) — slippage is worse, but counter-trend signals also stronger. Try grouping `is_profitable` by `entry_hour_utc` to see the U-shape.

### `market_id`

The market ID lets you cross-reference with Polymarket's gamma-api for richer metadata: category, end_date, current odds, etc. Example:

```python
import requests
mkt = requests.get(
    "https://gamma-api.polymarket.com/markets",
    params={"id": "544093"},
).json()
print(mkt[0]["category"], mkt[0]["endDate"])
```
