import os

BACKEND_API_BASE_URL = os.environ.get("BACKEND_API_BASE_URL", "http://host.docker.internal:8000")
MCP_PORT = int(os.environ.get("MCP_PORT", "8000"))
