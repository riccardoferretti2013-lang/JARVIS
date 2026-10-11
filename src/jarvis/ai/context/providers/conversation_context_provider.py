from ..context_block import ContextBlock
from ..sources import ConversationContextSource
from .context_provider import ContextProvider


class ConversationContextProvider(ContextProvider):
    """
    Trasforma la conversazione corrente
    in un ContextBlock.
    """

    def __init__(
        self,
        source: ConversationContextSource,
    ) -> None:

        self._source = source

    @property
    def provider_name(self) -> str:
        return "Conversation"

    @property
    def priority(self) -> int:
        return 80

    def get_context(
        self,
    ) -> ContextBlock:

        return ContextBlock(
            name=self.provider_name,
            priority=self.priority,
            messages=self._source.get_data(),
        )