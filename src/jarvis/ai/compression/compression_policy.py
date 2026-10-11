class CompressionPolicy:
    """
    Configura i limiti della compressione del contesto.
    """

    def __init__(
        self,
        max_characters: int = 12000,
        minimum_recent_messages: int = 6,
    ) -> None:
        if max_characters < 1000:
            raise ValueError(
                "max_characters deve essere almeno 1000."
            )

        if minimum_recent_messages < 1:
            raise ValueError(
                "minimum_recent_messages deve essere almeno 1."
            )

        self._max_characters = max_characters
        self._minimum_recent_messages = (
            minimum_recent_messages
        )

    @property
    def max_characters(self) -> int:
        return self._max_characters

    @property
    def minimum_recent_messages(self) -> int:
        return self._minimum_recent_messages

    def is_over_limit(
        self,
        character_count: int,
    ) -> bool:
        return character_count > self._max_characters