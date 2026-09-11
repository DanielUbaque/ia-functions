from mcp.server.fastmcp import FastMCP

from mcp_server.config import MCP_PORT
from mcp_server.tools.mediciones import consultar_promedio, consultar_ultima_medicion
from mcp_server.tools.mediciones_chat import confirmar_medicion, proponer_guardar_medicion
from mcp_server.tools.sitios import listar_sitios

app = FastMCP("colflux-backend", port=MCP_PORT)

app.add_tool(listar_sitios)
app.add_tool(consultar_promedio)
app.add_tool(consultar_ultima_medicion)
app.add_tool(proponer_guardar_medicion)
app.add_tool(confirmar_medicion)

if __name__ == "__main__":
    app.run(transport="streamable-http")
