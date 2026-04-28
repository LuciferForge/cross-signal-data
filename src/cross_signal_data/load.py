"""Loader for the bundled CSV dataset.

If pandas is installed, returns a DataFrame. Otherwise returns a list of dicts.
The dataset ships inside the package so `pip install cross-signal-data` is
self-contained — no external download.
"""
from __future__ import annotations

import csv
from importlib import resources
from pathlib import Path
from typing import Any

DATASET_VERSIONS = ["v1"]
LATEST = "v1"

# Map version → packaged data file
_VERSION_FILES = {
    "v1": "crashes_v1.csv",
}


# Schema definition (also documented in docs/schema.md)
SCHEMA = {
    "trade_id": ("int", "Sequential 0-indexed trade ID."),
    "market_id": ("str", "Polymarket market ID (public, queryable via gamma-api)."),
    "question": ("str", "Market question text at trade time."),
    "outcome_label": ("str", "YES/NO outcome the bot bet on."),
    "entry_time": ("str (ISO-8601 UTC)", "When the crash trigger fired."),
    "exit_time": ("str (ISO-8601 UTC)", "When the position closed."),
    "entry_price": ("float", "Per-share price at entry (0–1)."),
    "exit_price": ("float", "Per-share price at exit (0–1)."),
    "pre_crash_high": ("float", "Recent local-window high before the crash trigger."),
    "drop_pct": ("float", "(pre_crash_high − entry_price) / pre_crash_high × 100."),
    "size_usd": ("float", "USD allocated to the trade."),
    "shares": ("float", "Share count purchased."),
    "hold_hours": ("float", "Wall-clock hours from entry to exit."),
    "pnl_usd": ("float", "Realized P&L in USD (theoretical, not slippage-adjusted)."),
    "is_profitable": ("int (0/1)", "1 if pnl_usd > 0 else 0."),
    "exit_reason": ("str", "RECOVERY | TIMEOUT_48H | TIMEOUT | STOP."),
    "entry_hour_utc": ("int 0–23", "Hour-of-day at entry (UTC)."),
    "entry_dow": ("int 0–6", "Day-of-week at entry (0=Monday)."),
    "recovered_to_pct_of_high": ("float", "exit_price / pre_crash_high × 100."),
}

NUMERIC_COLS = {
    "trade_id": int,
    "entry_price": float,
    "exit_price": float,
    "pre_crash_high": float,
    "drop_pct": float,
    "size_usd": float,
    "shares": float,
    "hold_hours": float,
    "pnl_usd": float,
    "is_profitable": int,
    "entry_hour_utc": int,
    "entry_dow": int,
    "recovered_to_pct_of_high": float,
}


def _resolve_path(version: str) -> Path:
    """Find the CSV file. Looks in package data first, then ../data/ for dev installs."""
    if version not in _VERSION_FILES:
        raise ValueError(f"Unknown version {version!r}. Available: {DATASET_VERSIONS}")
    fname = _VERSION_FILES[version]

    # 1) Try packaged data
    try:
        with resources.as_file(resources.files("cross_signal_data").joinpath(f"data/{fname}")) as p:
            if p.exists():
                return p
    except (ModuleNotFoundError, FileNotFoundError):
        pass

    # 2) Fall back to repo-root layout (editable install)
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "data" / fname
        if candidate.exists():
            return candidate

    raise FileNotFoundError(f"Could not locate dataset file {fname}.")


def _read_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for col, caster in NUMERIC_COLS.items():
                if col in row and row[col] != "":
                    try:
                        row[col] = caster(row[col]) if caster is int else caster(row[col])
                    except ValueError:
                        row[col] = None
            rows.append(row)
    return rows


def load(version: str = LATEST, *, as_pandas: bool | None = None):
    """Load the dataset.

    Args:
        version: dataset version (default = latest, currently "v1").
        as_pandas: if True, return DataFrame (requires pandas).
            If False, return list of dicts.
            If None (default), return DataFrame if pandas is available, else list of dicts.

    Returns:
        pandas.DataFrame or list[dict].
    """
    path = _resolve_path(version)

    if as_pandas is None:
        try:
            import pandas as pd  # noqa: F401
            as_pandas = True
        except ImportError:
            as_pandas = False

    if as_pandas:
        import pandas as pd

        df = pd.read_csv(path)
        # Ensure dtypes
        for col, caster in NUMERIC_COLS.items():
            if col in df.columns:
                if caster is int:
                    df[col] = df[col].astype("Int64")
                else:
                    df[col] = df[col].astype(float)
        df["entry_time"] = pd.to_datetime(df["entry_time"], errors="coerce", utc=True)
        df["exit_time"] = pd.to_datetime(df["exit_time"], errors="coerce", utc=True)
        return df

    return _read_rows(path)


def list_versions() -> list[str]:
    """Return all available dataset versions."""
    return list(DATASET_VERSIONS)


def schema() -> dict:
    """Return column-name → (dtype, description) mapping."""
    return dict(SCHEMA)
