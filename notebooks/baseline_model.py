#!/usr/bin/env python3
"""Baseline model: predict `is_profitable` from feature columns.

Trains a logistic regression and a random forest on the dataset.
Reports cross-validated accuracy and feature importances.

Usage:
    pip install cross-signal-data[ml]
    python notebooks/baseline_model.py

The point isn't to beat 80% accuracy — the bot already enters with ~80% WR
based on the trigger alone. The point is to understand WHICH features carry
the predictive signal, so you can design a smarter trigger.
"""
from __future__ import annotations

import sys

try:
    import numpy as np
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
except ImportError:
    print("ERROR: install ML deps with: pip install cross-signal-data[ml]")
    sys.exit(1)

from cross_signal_data import load


def main():
    df = load()
    print(f"Loaded {len(df)} trades")
    print(f"Class balance: {df['is_profitable'].mean():.1%} profitable")
    print()

    # Feature set
    feature_cols = [
        "entry_price",
        "pre_crash_high",
        "drop_pct",
        "size_usd",
        "shares",
        "entry_hour_utc",
        "entry_dow",
    ]

    X = df[feature_cols].astype(float).values
    y = df["is_profitable"].astype(int).values

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # Logistic regression baseline
    lr_pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("lr", LogisticRegression(max_iter=1000, random_state=42)),
    ])
    lr_scores = cross_val_score(lr_pipe, X, y, cv=cv, scoring="accuracy", n_jobs=1)
    print(f"Logistic Regression: {lr_scores.mean():.3f} ± {lr_scores.std():.3f}")

    # Random forest
    rf = RandomForestClassifier(n_estimators=300, max_depth=6, random_state=42, n_jobs=1)
    rf_scores = cross_val_score(rf, X, y, cv=cv, scoring="accuracy", n_jobs=1)
    print(f"Random Forest:       {rf_scores.mean():.3f} ± {rf_scores.std():.3f}")

    # Train on full data for feature importance
    rf.fit(X, y)
    importances = sorted(
        zip(feature_cols, rf.feature_importances_),
        key=lambda x: -x[1],
    )

    print()
    print("Feature importance (random forest, full-data fit):")
    for name, imp in importances:
        bar = "█" * int(imp * 50)
        print(f"  {name:20} {imp:.4f}  {bar}")

    # Class-conditional means
    print()
    print("Mean of each feature by class:")
    print("=" * 70)
    grp = df.groupby("is_profitable")[feature_cols].mean().T
    print(grp.to_string(float_format=lambda v: f"{v:.3f}"))

    # Diurnal pattern
    print()
    print("Win rate by entry_hour_utc:")
    diurnal = df.groupby("entry_hour_utc")["is_profitable"].agg(["mean", "count"])
    print(diurnal.to_string())


if __name__ == "__main__":
    main()
