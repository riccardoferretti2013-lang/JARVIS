from ..conversation_manager import ConversationManager

from .conversation_summary import ConversationSummary
from .summary_policy import SummaryPolicy
from .summary_service import SummaryService


class SummaryManager:
    """
    Coordina la generazione automatica
    dei riassunti della conversazione.
    """

    def __init__(
        self,
        conversation_manager: ConversationManager,
        summary_service: SummaryService,
        policy: SummaryPolicy | None = None,
    ) -> None:
        self._conversation_manager = (
            conversation_manager
        )

        self._summary_service = (
            summary_service
        )

        self._policy = (
            policy
            or SummaryPolicy()
        )

    @property
    def summary_service(
        self,
    ) -> SummaryService:
        return self._summary_service

    @property
    def policy(
        self,
    ) -> SummaryPolicy:
        return self._policy

    def update_if_needed(
        self,
    ) -> ConversationSummary | None:
        messages = (
            self._conversation_manager
            .get_messages()
        )

        if not self._policy.should_summarize(
            len(messages)
        ):
            return None

        messages_to_summarize = (
            self._policy
            .get_messages_to_summarize(
                messages
            )
        )

        if not messages_to_summarize:
            return None

        summary = self._summary_service.summarize(
            messages_to_summarize
        )

        if summary is None:
            return None

        messages_to_keep = (
            self._policy
            .get_messages_to_keep(
                messages
            )
        )

        self._conversation_manager.replace_messages(
            messages_to_keep
        )

        return summary

    def get_summary(
        self,
    ) -> ConversationSummary | None:
        return (
            self._summary_service
            .get_summary()
        )

    def get_summary_content(
        self,
    ) -> str:
        return (
            self._summary_service
            .get_summary_content()
        )

    def clear(self) -> None:
        self._summary_service.clear()