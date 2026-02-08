"""Unified retrieval: sparse search and/or metadata filters."""
from typing import Any, Callable

from haystack.dataclasses import Document
from haystack import Pipeline
from haystack.components.retrievers.filter_retriever import FilterRetriever

MAX_TOP_K = 50
DEFAULT_TOP_K = 5

# Compound genre phrases → list of single-token genres (Qdrant meta.genre is keyword, no spaces)
COMPOUND_GENRE_MAP = {
    "romantic comedy": ["romance", "comedy"],
    "romance comedy": ["romance", "comedy"],
    "sci-fi": ["science fiction"],
    "science fiction": ["science fiction"],
    "action comedy": ["action", "comedy"],
    "drama comedy": ["drama", "comedy"],
    "black comedy": ["comedy"],
    "dark comedy": ["comedy"],
    "war drama": ["war", "drama"],
    "crime thriller": ["crime", "thriller"],
    "historical drama": ["history", "drama"],
    "romantic drama": ["romance", "drama"],
    "action thriller": ["action", "thriller"],
    "horror comedy": ["horror", "comedy"],
}
# Single-word synonyms when splitting unknown compounds (e.g. "historical romance" → history, romance)
WORD_TO_GENRE = {
    "romantic": "romance",
    "sci": "science fiction",
    "historical": "history",
    "fantasy": "fantasy",
    "animation": "animation",
    "animated": "animation",
}


def _normalize_metadata_filters(filters: dict[str, Any] | None) -> dict[str, Any] | None:
    """Expand compound genre values so Qdrant keyword index is used (avoids 400 text index error)."""
    if not filters or "conditions" not in filters:
        return filters
    conditions = filters.get("conditions") or []
    op = filters.get("operator", "AND")
    new_conditions = []
    for c in conditions:
        field = c.get("field")
        cond_op = c.get("operator")
        value = c.get("value")
        if field != "meta.genre" or cond_op != "==" or not isinstance(value, str):
            new_conditions.append(c)
            continue
        value_lower = value.strip().lower()
        if " " not in value_lower and value_lower not in COMPOUND_GENRE_MAP:
            new_conditions.append(c)
            continue
        if value_lower in COMPOUND_GENRE_MAP:
            tokens = COMPOUND_GENRE_MAP[value_lower]
        else:
            # Unknown compound: split on spaces, map known words via WORD_TO_GENRE, use rest as-is
            tokens = [WORD_TO_GENRE.get(w, w) for w in value_lower.split()]
        for token in tokens:
            new_conditions.append({"field": "meta.genre", "operator": "==", "value": token})
    return {"operator": op, "conditions": new_conditions}


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
        normalized_filters = _normalize_metadata_filters(metadata_filters)

        if query:
            result = sparse_pipeline.run(
                {
                    "sparse_text_embedder": {"text": query},
                    "sparse_retriever": {
                        "filters": normalized_filters,
                        "top_k": top_k,
                    },
                }
            )
            return result["sparse_retriever"]["documents"]

        documents = filter_retriever.run(filters=normalized_filters)["documents"]
        return documents[:top_k]

    return retrieval_function
