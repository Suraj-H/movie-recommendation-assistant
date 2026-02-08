"""Sparse query pipeline: text embedder → Qdrant sparse retriever."""
from haystack import Pipeline
from haystack_integrations.components.embedders.fastembed import FastembedSparseTextEmbedder
from haystack_integrations.components.retrievers.qdrant import QdrantSparseEmbeddingRetriever

from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

MODEL = "Qdrant/minicoil-v1"
DEFAULT_TOP_K = 5


def create_sparse_pipeline(
    document_store: QdrantDocumentStore,
    top_k: int = DEFAULT_TOP_K,
) -> Pipeline:
    pipeline = Pipeline()
    pipeline.add_component(
        "sparse_text_embedder",
        FastembedSparseTextEmbedder(model=MODEL),
    )
    pipeline.add_component(
        "sparse_retriever",
        QdrantSparseEmbeddingRetriever(document_store=document_store, top_k=top_k),
    )
    pipeline.connect(
        "sparse_text_embedder.sparse_embedding",
        "sparse_retriever.query_sparse_embedding",
    )
    return pipeline
