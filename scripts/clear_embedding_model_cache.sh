#!/usr/bin/env bash
# Remove cached Qdrant/minicoil-v1 embedding model from Hugging Face Hub cache.
# Used by indexing and query pipeline; will re-download on next index or query.
# Default: ~/.cache/huggingface/hub/
# Set HUGGINGFACE_HUB_CACHE to use a different cache location.

CACHE_DIR="${HUGGINGFACE_HUB_CACHE:-$HOME/.cache/huggingface/hub}"
find "$CACHE_DIR" -maxdepth 1 -type d -name '*minicoil*' -exec rm -rf {} + 2>/dev/null
echo "Done. Cleared minicoil embedding model cache under $CACHE_DIR"
