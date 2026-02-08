"""Unified retrieval: sparse search and/or metadata filters."""
from typing import Any, Callable

from haystack.dataclasses import Document
from haystack import Pipeline
from haystack.components.retrievers.filter_retriever import FilterRetriever

MAX_TOP_K = 50
DEFAULT_TOP_K = 5


def create_retrieval_function(
    sparse_pipeline: Pipeline,
    filter_retriever: FilterRetriever,
) -> Callable[..., list[Document]]:
    """Build retrieval_function that uses the given pipeline and filter retriever."""

    def retrieval_function(
        query: str | None = None,
        metadata_filters: dict[str, Any] | None = None,
        top_k: int = DEFAULT_TOP_K,
    ) -> list[Document]:
        if not query and not metadata_filters:
            raise ValueError(
                "At least one of 'query' or 'metadata_filters' must be provided."
            )
        effective_top_k = DEFAULT_TOP_K if top_k is None else top_k
        top_k = min(max(1, effective_top_k), MAX_TOP_K)

        if query:
            result = sparse_pipeline.run(
                {
                    "sparse_text_embedder": {"text": query},
                    "sparse_retriever": {
                        "filters": metadata_filters,
                        "top_k": top_k,
                    },
                }
            )
            return result["sparse_retriever"]["documents"]

        documents = filter_retriever.run(filters=metadata_filters)["documents"]
        return documents[:top_k]

    return retrieval_function
