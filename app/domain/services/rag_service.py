from app.domain.models import RetrievedChunk
from app.domain.ports.embedding_provider import EmbeddingProvider
from app.domain.ports.vector_store import VectorStore
from app.domain.services.chunking import chunk_text

DEFAULT_COLLECTION = "documents"


class RagService:
    def __init__(self, embeddings: EmbeddingProvider, vector_store: VectorStore) -> None:
        self._embeddings = embeddings
        self._vector_store = vector_store

    def ingest_document(self, source: str, text: str, collection: str = DEFAULT_COLLECTION) -> int:
        chunks = chunk_text(text)
        if not chunks:
            return 0
        embeddings = self._embeddings.embed(chunks)
        return self._vector_store.upsert(source, chunks, embeddings, collection)

    def retrieve(
        self,
        question: str,
        top_k: int,
        min_score: float,
        collection: str = DEFAULT_COLLECTION,
    ) -> list[RetrievedChunk]:
        query_embedding = self._embeddings.embed([question])[0]
        matches = self._vector_store.search(query_embedding, top_k, collection)
        return [m for m in matches if m.score >= min_score]
