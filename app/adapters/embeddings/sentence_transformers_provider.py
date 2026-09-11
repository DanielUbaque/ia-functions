from sentence_transformers import SentenceTransformer

from app.domain.ports.embedding_provider import EmbeddingProvider


class SentenceTransformersProvider(EmbeddingProvider):
    def __init__(self, model_name: str) -> None:
        self._model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts, normalize_embeddings=True).tolist()
