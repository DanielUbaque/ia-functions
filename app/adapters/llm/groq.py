from openai import OpenAI

from app.adapters.llm._openai_compat import (
    parse_openai_tool_calls,
    to_openai_messages,
    to_openai_tools,
    to_reply,
)
from app.config import settings
from app.domain.models import Message, ModelReply, ToolSpec
from app.domain.ports.llm_provider import LLMProvider


class GroqProvider(LLMProvider):
    def __init__(self) -> None:
        self._client = OpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        self._model = settings.groq_model

    def converse(
        self,
        messages: list[Message],
        tools: list[ToolSpec],
        system: str | None = None,
    ) -> ModelReply:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=to_openai_messages(messages, system),
            tools=to_openai_tools(tools) if tools else None,
            tool_choice="auto" if tools else None,
        )
        message = response.choices[0].message
        raw_tool_calls = [
            {"id": tc.id, "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
            for tc in (message.tool_calls or [])
        ]
        return to_reply(message.content, parse_openai_tool_calls(raw_tool_calls))
