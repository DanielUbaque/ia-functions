"""Traducción compartida entre proveedores que hablan el formato de tools
de OpenAI (Groq y Ollama)."""

import json

from app.domain.models import Message, ModelReply, ToolCall, ToolSpec


def to_openai_messages(messages: list[Message], system: str | None) -> list[dict]:
    out = []
    if system:
        out.append({"role": "system", "content": system})
    for m in messages:
        if m.role == "user":
            out.append({"role": "user", "content": m.text})
        elif m.role == "assistant":
            msg: dict = {"role": "assistant", "content": m.text or None}
            if m.tool_calls:
                msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.arguments, ensure_ascii=False),
                        },
                    }
                    for tc in m.tool_calls
                ]
            out.append(msg)
        elif m.role == "tool":
            out.append(
                {
                    "role": "tool",
                    "tool_call_id": m.tool_call_id,
                    "content": json.dumps(m.tool_result, ensure_ascii=False, default=str),
                }
            )
    return out


def to_openai_tools(tools: list[ToolSpec]) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
            },
        }
        for t in tools
    ]


def parse_openai_tool_calls(raw_tool_calls) -> list[ToolCall]:
    calls = []
    for tc in raw_tool_calls or []:
        try:
            arguments = json.loads(tc["function"]["arguments"] or "{}")
        except (ValueError, TypeError):
            arguments = {}
        calls.append(ToolCall(name=tc["function"]["name"], arguments=arguments, id=tc["id"]))
    return calls


def to_reply(text: str, tool_calls) -> ModelReply:
    return ModelReply(text=(text or "").strip(), tool_calls=tool_calls)
