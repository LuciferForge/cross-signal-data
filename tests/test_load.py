"""Smoke tests for the loader."""
from cross_signal_data import load, list_versions, schema


def test_list_versions():
    v = list_versions()
    assert isinstance(v, list)
    assert "v1" in v


def test_schema_returns_dict():
    s = schema()
    assert isinstance(s, dict)
    assert "trade_id" in s
    assert "is_profitable" in s
    assert "exit_reason" in s


def test_load_as_dicts_default():
    rows = load(as_pandas=False)
    assert isinstance(rows, list)
    assert len(rows) > 100  # we have 308 in v1
    assert "trade_id" in rows[0]
    assert "is_profitable" in rows[0]


def test_load_as_dicts_dtypes():
    rows = load(as_pandas=False)
    r = rows[0]
    # Numeric columns should be cast
    assert isinstance(r["entry_price"], float)
    assert isinstance(r["is_profitable"], int)
    assert isinstance(r["entry_hour_utc"], int)


def test_load_unknown_version():
    import pytest

    with pytest.raises(ValueError):
        load(version="v99")


def test_dataset_has_expected_columns():
    rows = load(as_pandas=False)
    r = rows[0]
    expected = {
        "trade_id", "market_id", "question", "outcome_label",
        "entry_time", "exit_time", "entry_price", "exit_price",
        "pre_crash_high", "drop_pct", "size_usd", "shares",
        "hold_hours", "pnl_usd", "is_profitable", "exit_reason",
        "entry_hour_utc", "entry_dow", "recovered_to_pct_of_high",
    }
    assert expected.issubset(set(r.keys()))


def test_load_pandas():
    """Optional — only runs if pandas is available."""
    try:
        import pandas as pd  # noqa
    except ImportError:
        return
    df = load()
    assert df.shape[0] > 100
    assert df.shape[1] >= 19
    # is_profitable should be 0/1
    assert df["is_profitable"].isin([0, 1]).all()


def test_dataset_invariants():
    """Validate sanity invariants on the actual data."""
    rows = load(as_pandas=False)
    for r in rows:
        # Polymarket prices are 0–1 probabilities
        assert 0 < r["entry_price"] <= 1, f"bad entry_price: {r['entry_price']}"
        assert 0 < r["exit_price"] <= 1, f"bad exit_price: {r['exit_price']}"
        # pre_crash_high should be >= entry_price (it's a recent high)
        assert r["pre_crash_high"] >= r["entry_price"] - 1e-6
        # is_profitable should be consistent with pnl
        if r["pnl_usd"] > 0:
            assert r["is_profitable"] == 1
        else:
            assert r["is_profitable"] == 0
