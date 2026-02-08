#!/usr/bin/env bash
# Remove cached Pablinho/movies-dataset from Hugging Face cache.
# Default cache: ~/.cache/huggingface/datasets/
# Set HF_DATASETS_CACHE to use a different cache location.

CACHE_DIR="${HF_DATASETS_CACHE:-$HOME/.cache/huggingface/datasets}"
find "$CACHE_DIR" -maxdepth 2 -type d -name '*Pablinho*movies*' -exec rm -rf {} + 2>/dev/null
echo "Done. Cleared Pablinho/movies-dataset cache under $CACHE_DIR"
