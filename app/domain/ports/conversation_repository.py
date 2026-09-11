from abc import ABC, abstractmethod

from app.domain.models import Message, PendingConfirmation


class ConversationRepository(ABC):
    @abstractmethod
    def recent_messages(self, external_user_id: str, limit: int, minutes: int) -> list[Message]:
        raise NotImplementedError

    @abstractmethod
    def save_turn(
        self,
        external_user_id: str,
        question: str,
        answer: str,
        tools_used: list[str],
        pending: PendingConfirmation | None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def latest_pending(self, external_user_id: str) -> PendingConfirmation | None:
        raise NotImplementedError

    @abstractmethod
    def resolve_pending(self, pending_id: str) -> None:
        raise NotImplementedError
