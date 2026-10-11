from dataclasses import dataclass

from ..provider import Message


@dataclass(frozen=True, slots=True)
class CompressionResult:
    """
    Risultato della compressione del contesto.
    """

    messages: list[Message]
    original_characters: int
    final_characters: int
    removed_messages: int

    @property
    def was_compressed(self) -> bool:
        return self.removed_messages > 0

    @property
    def saved_characters(self) -> int:
        return max(
            0,
            self.original_characters
            - self.final_characters,
        )