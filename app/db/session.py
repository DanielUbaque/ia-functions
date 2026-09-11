import psycopg
from pgvector.psycopg import register_vector

from app.config import settings

EMBEDDING_DIM = 384  # all-MiniLM-L6-v2


def get_connection() -> psycopg.Connection:
    conn = psycopg.connect(settings.database_url, autocommit=True)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    return conn


def init_schema() -> None:
    with get_connection() as conn:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id SERIAL PRIMARY KEY,
                source TEXT NOT NULL,
                content TEXT NOT NULL,
                collection TEXT NOT NULL DEFAULT 'documents',
                embedding VECTOR({EMBEDDING_DIM}) NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS document_chunks_collection_idx "
            "ON document_chunks (collection)"
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                external_user_id TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                external_user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                tools_used TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS messages_user_idx "
            "ON messages (external_user_id, created_at)"
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pending_confirmations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                external_user_id TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                arguments JSONB NOT NULL,
                resolved BOOLEAN NOT NULL DEFAULT false,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS pending_confirmations_user_idx "
            "ON pending_confirmations (external_user_id, resolved, created_at)"
        )
