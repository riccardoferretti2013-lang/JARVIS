from ...conversation_manager import ConversationManager
from ...provider import Message

from .context_source import ContextSource


class ConversationContextSource(ContextSource):
    """
    Fornisce i messaggi della conversazione.
    """

    def __init__(
        self,
        conversation_manager: ConversationManager,
    ) -> None:

        self._conversation_manager = (
            conversation_manager
        )

    @property
    def source_name(self) -> str:
        return "Conversation"

    def get_data(
        self,
    ) -> list[Message]:

        return (
            self._conversation_manager
            .get_messages()
        )