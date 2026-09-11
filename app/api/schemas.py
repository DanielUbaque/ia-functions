from typing import Any

from pydantic import BaseModel


class IngestRequest(BaseModel):
    source: str
    text: str
    collection: str = "documents"


class IngestResponse(BaseModel):
    chunks_indexed: int


class ChatRequest(BaseModel):
    message: str
    usuario: str = "anonimo"


class Source(BaseModel):
    source: str
    content: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    herramientas: list[str] = []
    pendiente_de_confirmacion: dict[str, Any] | None = None


class HistorialMessage(BaseModel):
    role: str
    content: str


class HistorialResponse(BaseModel):
    messages: list[HistorialMessage]
