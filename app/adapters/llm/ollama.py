import requests

from app.adapters.llm._openai_compat import to_openai_messages, to_openai_tools, to_reply
from app.config import settings
from app.domain.models import Message, ModelReply, ToolCall, ToolSpec
from app.domain.ports.llm_provider import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self) -> None:
        self._base_url = settings.ollama_base_url
        self._model = settings.ollama_model

    def converse(
        self,
        messages: list[Message],
        tools: list[ToolSpec],
        system: str | None = None,
    ) -> ModelReply:
        response = requests.post(
            f"{self._base_url}/api/chat",
            json={
                "model": self._model,
                "messages": to_openai_messages(messages, system),
                "tools": to_openai_tools(tools) if tools else None,
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
        message = response.json().get("message", {})

        # A diferencia de OpenAI/Groq, Ollama devuelve los argumentos de cada
        # tool_call ya como dict, no como string JSON.
        tool_calls = [
            ToolCall(name=tc["function"]["name"], arguments=tc["function"].get("arguments") or {})
            for tc in message.get("tool_calls") or []
        ]
        return to_reply(message.get("content", ""), tool_calls)
