"""cross-signal-data — Polymarket crash-recovery labeled dataset.

Quick start:
    from cross_signal_data import load
    df = load()
    print(df.head())

Returns a pandas DataFrame with one row per closed crash-recovery trade
on Polymarket. See docs/schema.md for column definitions.
"""
from cross_signal_data.load import load, list_versions, schema

__version__ = "0.1.0"
__all__ = ["load", "list_versions", "schema", "__version__"]
