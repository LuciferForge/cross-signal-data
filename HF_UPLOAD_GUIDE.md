# Uploading to HuggingFace Datasets

After the GitHub repo is set up, mirror the dataset on HuggingFace for the ML/DS audience that lives on HF.

## One-time setup

```bash
pip install huggingface_hub datasets
huggingface-cli login   # paste your HF write token
```

## Push the dataset

```bash
huggingface-cli upload \
    LuciferForge/cross-signal-data \
    data/crashes_v1.csv \
    data/crashes_v1.csv \
    --repo-type=dataset
```

Or via the Python API:

```python
from huggingface_hub import HfApi

api = HfApi()
api.create_repo(
    repo_id="LuciferForge/cross-signal-data",
    repo_type="dataset",
    exist_ok=True,
)
api.upload_file(
    path_or_fileobj="data/crashes_v1.csv",
    path_in_repo="data/crashes_v1.csv",
    repo_id="LuciferForge/cross-signal-data",
    repo_type="dataset",
)
api.upload_file(
    path_or_fileobj="README.md",
    path_in_repo="README.md",
    repo_id="LuciferForge/cross-signal-data",
    repo_type="dataset",
)
```

## Dataset card

HuggingFace expects a YAML frontmatter at the top of the README for proper indexing. Add this when uploading the dataset card:

```yaml
---
license: mit
task_categories:
  - tabular-classification
language:
  - en
tags:
  - polymarket
  - prediction-markets
  - trading
  - mean-reversion
  - finance
size_categories:
  - n<1K
---
```

## Why mirror

GitHub captures the developer audience. HuggingFace captures the ML researcher audience. Both are valuable and the cost of mirroring is ~5 minutes.

The HF link goes in:
- Tweet announcing the dataset
- The repo README "Also available on HuggingFace" section
- Any blog post discussing the dataset
