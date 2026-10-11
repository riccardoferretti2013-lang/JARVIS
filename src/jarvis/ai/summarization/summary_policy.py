class SummaryPolicy:
    """
    Decide quando creare un nuovo riassunto.
    """

    def __init__(
        self,
        message_threshold: int = 20,
        messages_to_keep: int = 8,
    ) -> None:
        if message_threshold < 2:
            raise ValueError(
                "message_threshold deve essere almeno 2."
            )

        if messages_to_keep < 1:
            raise ValueError(
                "messages_to_keep deve essere almeno 1."
            )

        if messages_to_keep >= message_threshold:
            raise ValueError(
                "messages_to_keep deve essere minore "
                "di message_threshold."
            )

        self._message_threshold = message_threshold
        self._messages_to_keep = messages_to_keep

    @property
    def message_threshold(self) -> int:
        return self._message_threshold

    @property
    def messages_to_keep(self) -> int:
        return self._messages_to_keep

    def should_summarize(
        self,
        message_count: int,
    ) -> bool:
        return message_count >= self._message_threshold

    def get_messages_to_summarize(
        self,
        messages: list[dict],
    ) -> list[dict]:
        if len(messages) <= self._messages_to_keep:
            return []

        return messages[
            :-self._messages_to_keep
        ]

    def get_messages_to_keep(
        self,
        messages: list[dict],
    ) -> list[dict]:
        return messages[
            -self._messages_to_keep:
        ]