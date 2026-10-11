from ..provider import Message

from .compression_policy import CompressionPolicy
from .compression_result import CompressionResult


class ContextCompressor:
    """
    Comprime il contesto mantenendo
    i messaggi più importanti.
    """

    def __init__(
        self,
        policy: CompressionPolicy | None = None,
    ) -> None:
        self._policy = (
            policy
            or CompressionPolicy()
        )

    @property
    def policy(
        self,
    ) -> CompressionPolicy:
        return self._policy

    def compress(
        self,
        messages: list[Message],
    ) -> CompressionResult:
        """
        Comprime il contesto se supera il limite.
        """

        copied_messages = list(messages)

        original_characters = self._character_count(
            copied_messages
        )

        if not self._policy.is_over_limit(
            original_characters
        ):
            return CompressionResult(
                messages=copied_messages,
                original_characters=original_characters,
                final_characters=original_characters,
                removed_messages=0,
            )

        compressed = self._compress_messages(
            copied_messages
        )

        final_characters = self._character_count(
            compressed
        )

        return CompressionResult(
            messages=compressed,
            original_characters=original_characters,
            final_characters=final_characters,
            removed_messages=(
                len(messages)
                - len(compressed)
            ),
        )

    def _compress_messages(
        self,
        messages: list[Message],
    ) -> list[Message]:
        """
        Mantiene:
        - tutti i messaggi system;
        - gli ultimi N messaggi;
        """

        recent_messages = (
            self._policy.minimum_recent_messages
        )

        system_messages = [
            message
            for message in messages
            if message.get("role") == "system"
        ]

        normal_messages = [
            message
            for message in messages
            if message.get("role") != "system"
        ]

        if (
            len(normal_messages)
            <= recent_messages
        ):
            return messages

        return (
            system_messages
            + normal_messages[-recent_messages:]
        )

    @staticmethod
    def _character_count(
        messages: list[Message],
    ) -> int:
        total = 0

        for message in messages:
            content = str(
                message.get(
                    "content",
                    "",
                )
                or ""
            )

            total += len(content)

        return total