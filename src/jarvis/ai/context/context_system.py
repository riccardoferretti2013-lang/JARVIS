from ..provider import Message

from .context_block import ContextBlock
from .registry import ContextProviderRegistry


class ContextSystem:
    """
    Costruisce il contesto finale da inviare all'AI.
    """

    def __init__(
        self,
        registry: ContextProviderRegistry,
    ) -> None:

        self._registry = registry

    @property
    def registry(
        self,
    ) -> ContextProviderRegistry:
        return self._registry

    def build(
        self,
    ) -> list[Message]:

        blocks: list[ContextBlock] = []

        for provider in self._registry.providers:
            block = provider.get_context()

            if (
                block.enabled
                and block.messages
            ):
                blocks.append(block)

        blocks.sort(
            key=lambda block: block.priority,
            reverse=True,
        )

        messages: list[Message] = []

        for block in blocks:
            messages.extend(block.messages)

        return messages