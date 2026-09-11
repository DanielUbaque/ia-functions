from abc import ABC, abstractmethod

from app.domain.models import RetrievedChunk


class VectorStore(ABC):
    @abstractmethod
    def upsert(
        self,
        source: str,
        chunks: list[str],
        embeddings: list[list[float]],
        collection: str,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        top_k: int,
        collection: str,
    ) -> list[RetrievedChunk]:
        raise NotImplementedError
