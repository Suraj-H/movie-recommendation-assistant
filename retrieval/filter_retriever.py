"""Filter-only retriever for metadata queries."""
from haystack.components.retrievers.filter_retriever import FilterRetriever
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore


def create_filter_retriever(document_store: QdrantDocumentStore) -> FilterRetriever:
    return FilterRetriever(document_store=document_store)
