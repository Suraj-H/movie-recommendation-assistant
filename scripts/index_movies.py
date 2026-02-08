#!/usr/bin/env python3
"""Index movies: load dataset → documents → sparse embed → Qdrant."""
import argparse
import logging
import sys
import time
from pathlib import Path

# Ensure project root is on path (works when run from any CWD or via IDE)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datasets import load_dataset

from config import get_settings
from data import movie_to_document
from indexing import SparseDocumentEmbedder, create_document_store

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DATASET_NAME = "Pablinho/movies-dataset"
SPLIT = "train"
BATCH_LOG_INTERVAL = 500


def main() -> None:
    parser = argparse.ArgumentParser(description="Index movies into Qdrant with sparse embeddings.")
    parser.add_argument(
        "--recreate",
        action="store_true",
        default=True,
        help="Recreate index (default: True). Set --no-recreate to keep existing index.",
    )
    parser.add_argument("--no-recreate", action="store_false", dest="recreate", help="Keep existing index.")
    args = parser.parse_args()

    settings = get_settings()
    settings.require_qdrant()

    logger.info("Loading dataset %s (%s)...", DATASET_NAME, SPLIT)
    dataset = load_dataset(
        DATASET_NAME,
        split=SPLIT,
        token=settings.hf_token or None,
    )
    documents = movie_to_document(dataset)
    logger.info("Converted %d movies to documents.", len(documents))

    logger.info("Warming up sparse embedder...")
    embedder = SparseDocumentEmbedder()
    embedder.warm_up()

    logger.info("Embedding %d documents...", len(documents))
    t0 = time.perf_counter()
    embedded = embedder.run(documents)
    elapsed = time.perf_counter() - t0
    logger.info("Embedded in %.2f s (%.1f docs/s).", elapsed, len(embedded) / elapsed if elapsed else 0)

    logger.info("Creating document store (recreate_index=%s)...", args.recreate)
    store = create_document_store(settings, recreate_index=args.recreate)
    logger.info("Writing %d documents to Qdrant...", len(embedded))
    store.write_documents(documents=embedded)
    logger.info("Indexing complete.")


if __name__ == "__main__":
    main()
    sys.exit(0)
