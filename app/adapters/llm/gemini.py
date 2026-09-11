from app.config import settings
from app.domain.models import Message, ModelReply, ToolCall, ToolSpec
from app.domain.ports.llm_provider import LLMProvider

_JSON_SCHEMA_TYPES = {
    "object": "OBJECT",
    "string": "STRING",
    "number": "NUMBER",
    "integer": "INTEGER",
    "boolean": "BOOLEAN",
    "array": "ARRAY",
}


class GeminiProvider(LLMProvider):
    def __init__(self) -> None:
        self._api_key = settings.gemini_api_key
        self._model = settings.gemini_model

    def _client(self):
        from google import genai

        return genai.Client(api_key=self._api_key)

    def _to_schema(self, spec: dict):
        from google.genai import types

        kwargs = {"type": _JSON_SCHEMA_TYPES.get(spec.get("type", "string"), "STRING")}
        if spec.get("description"):
            kwargs["description"] = spec["description"]
        if spec.get("enum"):
            kwargs["enum"] = list(spec["enum"])
        if spec.get("properties"):
            kwargs["properties"] = {k: self._to_schema(v) for k, v in spec["properties"].items()}
        if spec.get("required"):
            kwargs["required"] = list(spec["required"])
        if spec.get("items"):
            kwargs["items"] = self._to_schema(spec["items"])
        return types.Schema(**kwargs)

    def _to_contents(self, messages: list[Message]):
        from google.genai import types

        contents = []
        for m in messages:
            if m.role == "user":
                contents.append(types.Content(role="user", parts=[types.Part(text=m.text)]))
            elif m.role == "assistant":
                parts = []
                if m.text:
                    parts.append(types.Part(text=m.text))
                for tc in m.tool_calls:
                    parts.append(types.Part(function_call=types.FunctionCall(name=tc.name, args=tc.arguments)))
                if parts:
                    contents.append(types.Content(role="model", parts=parts))
            elif m.role == "tool":
                contents.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_function_response(
                                name=m.tool_name, response={"result": m.tool_result}
                            )
                        ],
                    )
                )
        return contents

    def converse(
        self,
        messages: list[Message],
        tools: list[ToolSpec],
        system: str | None = None,
    ) -> ModelReply:
        from google.genai import types

        declarations = [
            types.FunctionDeclaration(
                name=t.name, description=t.description, parameters=self._to_schema(t.parameters)
            )
            for t in tools
        ]
        config = types.GenerateContentConfig(
            system_instruction=system,
            tools=[types.Tool(function_declarations=declarations)] if declarations else None,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

        response = self._client().models.generate_content(
            model=self._model,
            contents=self._to_contents(messages),
            config=config,
        )

        tool_calls = [
            ToolCall(name=fc.name, arguments=dict(fc.args or {}))
            for fc in (response.function_calls or [])
        ]
        return ModelReply(text=(response.text or "").strip(), tool_calls=tool_calls)
