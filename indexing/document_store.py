"""Qdrant document store with sparse embeddings and payload indexes."""
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack.utils import Secret

from config.settings import Settings

PAYLOAD_FIELDS = [
    {"field_name": "meta.language", "field_schema": "keyword"},
    {"field_name": "meta.rating", "field_schema": "float"},
    {"field_name": "meta.genre", "field_schema": "keyword"},
    {"field_name": "meta.title", "field_schema": "keyword"},
]


def create_document_store(
    settings: Settings,
    *,
    recreate_index: bool = True,
) -> QdrantDocumentStore:
    settings.require_qdrant()
    return QdrantDocumentStore(
        url=settings.qdrant_url,
        index=settings.qdrant_index_name,
        api_key=Secret.from_token(settings.qdrant_api_key),
        use_sparse_embeddings=True,
        recreate_index=recreate_index,
        payload_fields_to_index=PAYLOAD_FIELDS,
    )
