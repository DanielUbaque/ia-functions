from abc import ABC, abstractmethod
from typing import Any

from app.domain.models import ToolSpec


class ToolProvider(ABC):
    """Fuente de herramientas para el orquestador. Puede ser local (RAG, en
    el mismo proceso) o remota (un servidor MCP)."""

    @abstractmethod
    def list_tools(self) -> list[ToolSpec]:
        raise NotImplementedError

    @abstractmethod
    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
