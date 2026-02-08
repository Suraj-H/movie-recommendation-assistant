#!/usr/bin/env python3
"""Verify setup: imports and config load. No Qdrant/OpenAI calls."""
import sys
from pathlib import Path

def main():
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from config import get_settings
    from data import movie_to_document, movie_to_string
    from indexing import SparseDocumentEmbedder, create_document_store
    from retrieval import create_sparse_pipeline, create_filter_retriever, create_retrieval_function
    from tools import RETRIEVAL_TOOL_PARAMETERS, create_retrieval_tool
    from agent import SYSTEM_PROMPT, create_movie_agent, build_movie_agent
    from app.main import app
    from app.schemas import QueryRequest, QueryResponse
    s = get_settings()
    assert hasattr(s, "openai_api_key") and hasattr(s, "qdrant_url")
    print("OK: All imports and config load succeeded. Run index_movies then query_agent or API with .env set.")

if __name__ == "__main__":
    main()
