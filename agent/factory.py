"""Build the movie agent once; shared by CLI and API. Fails fast if config invalid."""
from config import get_settings
from indexing.document_store import create_document_store
from retrieval import (
    create_sparse_pipeline,
    create_filter_retriever,
    create_retrieval_function,
)
from tools import create_retrieval_tool
from agent.movie_agent import create_movie_agent


def build_movie_agent():
    """Create store, pipeline, retriever, tool, and agent. Raises if env invalid."""
    settings = get_settings()
    settings.require_openai()
    settings.require_qdrant()

    store = create_document_store(settings, recreate_index=False)
    pipeline = create_sparse_pipeline(store)
    filter_retriever = create_filter_retriever(store)
    retrieval_fn = create_retrieval_function(pipeline, filter_retriever)
    tool = create_retrieval_tool(retrieval_fn)
    return create_movie_agent(tool)
