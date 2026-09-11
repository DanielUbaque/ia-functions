"""Formato neutro del dominio: ni el orquestador ni las tools conocen el
formato propio de ningún proveedor de LLM ni de ningún transporte (HTTP,
MCP). Los adaptadores traducen desde/hacia estos tipos."""

from dataclasses import dataclass, field
from typing import Any
import uuid


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])


@dataclass
class Message:
    role: str  # "user" | "assistant" | "tool"
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_call_id: str | None = None
    tool_name: str | None = None
    tool_result: dict[str, Any] | None = None


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema


@dataclass
class ModelReply:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)


@dataclass
class Chunk:
    source: str
    content: str
    collection: str = "documents"


@dataclass
class RetrievedChunk:
    source: str
    content: str
    score: float


@dataclass
class PendingConfirmation:
    id: str
    tool_name: str
    arguments: dict[str, Any]
