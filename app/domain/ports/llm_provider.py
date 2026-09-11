from abc import ABC, abstractmethod

from app.domain.models import Message, ModelReply, ToolSpec


class LLMProvider(ABC):
    @abstractmethod
    def converse(
        self,
        messages: list[Message],
        tools: list[ToolSpec],
        system: str | None = None,
    ) -> ModelReply:
        """Un turno de conversación. Si el modelo decide usar una o más
        tools, vienen en ModelReply.tool_calls; quien llama es responsable
        de ejecutarlas y de agregar el resultado como un nuevo Message con
        role="tool" antes de volver a llamar a converse()."""
        raise NotImplementedError
