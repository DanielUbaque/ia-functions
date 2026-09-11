import json

from app.db.session import get_connection
from app.domain.models import Message, PendingConfirmation
from app.domain.ports.conversation_repository import ConversationRepository


class PostgresConversationRepository(ConversationRepository):
    def recent_messages(self, external_user_id: str, limit: int, minutes: int) -> list[Message]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT role, content FROM messages
                    WHERE external_user_id = %s
                      AND created_at >= now() - (%s || ' minutes')::interval
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (external_user_id, minutes, limit * 2),
                )
                rows = cur.fetchall()
        return [Message(role=role, text=content) for role, content in reversed(rows)]

    def save_turn(
        self,
        external_user_id: str,
        question: str,
        answer: str,
        tools_used: list[str],
        pending: PendingConfirmation | None,
    ) -> None:
        tools_csv = ", ".join(dict.fromkeys(tools_used))[:200]
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO messages (external_user_id, role, content, tools_used) VALUES (%s, 'user', %s, '')",
                    (external_user_id, question),
                )
                cur.execute(
                    "INSERT INTO messages (external_user_id, role, content, tools_used) VALUES (%s, 'assistant', %s, %s)",
                    (external_user_id, answer, tools_csv),
                )
                if pending:
                    cur.execute(
                        "INSERT INTO pending_confirmations (external_user_id, tool_name, arguments) "
                        "VALUES (%s, %s, %s)",
                        (external_user_id, pending.tool_name, json.dumps(pending.arguments, default=str)),
                    )

    def latest_pending(self, external_user_id: str) -> PendingConfirmation | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, tool_name, arguments FROM pending_confirmations
                    WHERE external_user_id = %s AND resolved = false
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (external_user_id,),
                )
                row = cur.fetchone()
        if not row:
            return None
        return PendingConfirmation(id=str(row[0]), tool_name=row[1], arguments=row[2])

    def resolve_pending(self, pending_id: str) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE pending_confirmations SET resolved = true WHERE id = %s",
                    (pending_id,),
                )
