# colflux · IA engine

Motor de IA de colflux: un agente con RAG + tool-calling sobre datos de
carbono, pensado para integrarse con un chat externo (web, WhatsApp, Slack,
etc.). Arquitectura hexagonal — ver [arquitectura.md](./arquitectura.md)
para el diagrama de componentes y el detalle de cada funcionalidad.

## Arquitectura

- **API**: FastAPI (`app/main.py`), expone `POST /ingest`, `POST /chat` y
  `GET /chat/historial`.
- **Núcleo hexagonal** (`app/domain/`): puertos + servicios (RAG, tool
  registry, orquestador), sin dependencias de frameworks.
- **Adaptadores** (`app/adapters/`): implementaciones concretas de cada
  puerto (LLM, embeddings, vector store, tools, persistencia). El
  `app/bootstrap/container.py` decide cuál usar según `.env`.
- **Vector store**: Postgres + [pgvector](https://github.com/pgvector/pgvector).
- **Embeddings**: `sentence-transformers` (modelo local, gratis, offline).
- **LLM**: intercambiable vía la variable `LLM_PROVIDER`, con tool-calling
  para los 4 proveedores en `app/adapters/llm/`:
  - `groq` (default, free tier, recomendado para empezar sin costo)
  - `gemini`
  - `ollama` (modelo local en Docker, 100% gratis y offline)
  - `anthropic`

  Cambiar de proveedor no requiere tocar código, solo `LLM_PROVIDER` y su
  API key correspondiente en `.env`.
- **`mcp_server/`**: servidor MCP aparte que expone datos del backend
  Django (sitios, mediciones) como tools, consumiendo su API pública por
  HTTP. Se registra en `MCP_SERVERS`; si no está disponible, el agente
  sigue funcionando solo con RAG.

## Requisitos

- Docker y Docker Compose

## Uso

```bash
cp .env.example .env
# Completa al menos GROQ_API_KEY (https://console.groq.com) o cambia
# LLM_PROVIDER a otro proveedor.

docker compose up -d db api mcp-backend
```

La API queda disponible en `http://localhost:8001`. `mcp-backend` requiere
que `BACKEND_API_BASE_URL` apunte a un backend Django corriendo (local o
desplegado); si no lo tienes disponible, omite ese servicio y deja
`MCP_SERVERS` vacío en `.env` — el agente sigue funcionando solo con RAG.

Si quieres usar Ollama en vez de una API externa:

```bash
docker compose --profile ollama up -d db api ollama
# Descarga el modelo dentro del contenedor:
docker compose exec ollama ollama pull llama3.1
# Y en .env: LLM_PROVIDER=ollama
```

### Endpoints

- `GET /health` — chequeo de salud.
- `POST /ingest` — indexa un documento en una colección (`documents` por
  defecto, o `dictionary` para el diccionario de campo).
  ```json
  {"source": "reporte-2024.pdf", "text": "...", "collection": "documents"}
  ```
- `POST /chat` — le habla al agente (RAG + tools, si hay un `mcp-backend`
  registrado).
  ```json
  {"message": "¿Cuál es el promedio de CO2 en Chingaza?", "usuario": "web-123"}
  ```
- `GET /chat/historial?usuario=web-123` — últimos turnos de esa persona.

## Desarrollo local

El servicio `api` monta `./app` como volumen y `mcp-backend` monta
`./mcp_server`, así que los cambios de código se reflejan sin reconstruir la
imagen (reinicia el contenedor correspondiente para que se recarguen:
`docker compose restart api mcp-backend`).
