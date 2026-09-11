import json

import anthropic

from app.config import settings
from app.domain.models import Message, ModelReply, ToolCall, ToolSpec
from app.domain.ports.llm_provider import LLMProvider


def _to_anthropic_messages(messages: list[Message]) -> list[dict]:
    out: list[dict] = []
    for m in messages:
        if m.role == "user":
            out.append({"role": "user", "content": m.text})
        elif m.role == "assistant":
            content = []
            if m.text:
                content.append({"type": "text", "text": m.text})
            for tc in m.tool_calls:
                content.append({"type": "tool_use", "id": tc.id, "name": tc.name, "input": tc.arguments})
            out.append({"role": "assistant", "content": content})
        elif m.role == "tool":
            block = {
                "type": "tool_result",
                "tool_use_id": m.tool_call_id,
                "content": json.dumps(m.tool_result, ensure_ascii=False, default=str),
            }
            # Anthropic exige que todos los tool_result de un mismo turno del
            # modelo viajen juntos en un único mensaje "user".
            if out and out[-1]["role"] == "user" and isinstance(out[-1]["content"], list):
                out[-1]["content"].append(block)
            else:
                out.append({"role": "user", "content": [block]})
    return out


def _to_anthropic_tools(tools: list[ToolSpec]) -> list[dict]:
    return [
        {"name": t.name, "description": t.description, "input_schema": t.parameters}
        for t in tools
    ]


class AnthropicProvider(LLMProvider):
    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self._model = settings.anthropic_model

    def converse(
        self,
        messages: list[Message],
        tools: list[ToolSpec],
        system: str | None = None,
    ) -> ModelReply:
        kwargs = {}
        if tools:
            kwargs["tools"] = _to_anthropic_tools(tools)

        response = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=system or "",
            messages=_to_anthropic_messages(messages),
            **kwargs,
        )

        text = "".join(b.text for b in response.content if b.type == "text")
        tool_calls = [
            ToolCall(name=b.name, arguments=b.input, id=b.id)
            for b in response.content
            if b.type == "tool_use"
        ]
        return ModelReply(text=text.strip(), tool_calls=tool_calls)
