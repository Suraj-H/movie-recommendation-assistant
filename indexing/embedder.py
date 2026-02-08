"""Sparse document embedder (minicoil-v1) for indexing."""
from haystack.dataclasses import Document
from haystack_integrations.components.embedders.fastembed import FastembedSparseDocumentEmbedder


class SparseDocumentEmbedder:
    """Wraps FastembedSparseDocumentEmbedder with fixed model and meta fields."""

    MODEL = "Qdrant/minicoil-v1"
    META_FIELDS = ["title"]

    def __init__(self) -> None:
        self._embedder = FastembedSparseDocumentEmbedder(
            model=self.MODEL,
            meta_fields_to_embed=self.META_FIELDS,
        )

    def warm_up(self) -> None:
        self._embedder.warm_up()

    def run(self, documents: list[Document]) -> list[Document]:
        result = self._embedder.run(documents=documents)
        return result["documents"]
