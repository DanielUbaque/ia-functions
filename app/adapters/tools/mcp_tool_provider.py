"""Cliente MCP genérico: se conecta a un servidor MCP remoto (protocolo
MCP sobre HTTP), descubre sus tools y las expone como un ToolProvider más.
El orquestador no sabe que esto es HTTP ni que hay un proceso aparte detrás
— para él es una tool igual que cualquier otra."""

import asyncio
import json
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from app.domain.models import ToolSpec
from app.domain.ports.tool_provider import ToolProvider


class McpToolProvider(ToolProvider):
    def __init__(self, url: str) -> None:
        self._url = url
        self._specs = asyncio.run(self._fetch_tools())

    async def _fetch_tools(self) -> list[ToolSpec]:
        async with streamablehttp_client(self._url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                return [
                    ToolSpec(name=t.name, description=t.description or "", parameters=t.inputSchema)
                    for t in result.tools
                ]

    def list_tools(self) -> list[ToolSpec]:
        return self._specs

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return asyncio.run(self._call_tool(name, arguments))

    async def _call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        async with streamablehttp_client(self._url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments)
                text = "".join(block.text for block in result.content if block.type == "text")
        if not text:
            return {}
        try:
            return json.loads(text)
        except ValueError:
            return {"result": text}
