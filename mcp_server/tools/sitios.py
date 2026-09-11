from mcp_server import backend_client


def listar_sitios(filtro: str | None = None) -> dict:
    """Lista los sitios de monitoreo con sus coordenadas, vía la API pública
    del backend (GET /api/geo/sitios/)."""
    sitios = backend_client.get_sitios(filtro)
    return {"total": len(sitios), "sitios": sitios}
