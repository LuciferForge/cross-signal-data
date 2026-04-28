# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-04-28

### Added
- Initial public release of `crashes_v1.csv`.
- 308 closed Polymarket crash-recovery trades, 80.2% profitable.
- Date range: March 2026 – April 2026.
- 19 columns (market metadata, signal features, outcome labels, time features).
- Python loader bundled in package: `from cross_signal_data import load`.
- Pandas optional via `pip install cross-signal-data[pandas]`.
- ML notebook + scikit-learn baseline via `pip install cross-signal-data[ml]`.
  - Logistic regression and random forest both achieve ~79.9% CV accuracy.
- HuggingFace dataset mirror: [huggingface.co/datasets/LuciferForge/cross-signal-data](https://huggingface.co/datasets/LuciferForge/cross-signal-data).
- 8/8 unit tests including data invariants (price ≤ 1, profitability consistency).
- MIT license (code and data).

[0.1.0]: https://github.com/LuciferForge/cross-signal-data/releases/tag/v0.1.0
