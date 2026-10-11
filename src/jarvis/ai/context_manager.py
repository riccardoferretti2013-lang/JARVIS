from copy import deepcopy

from .provider import Message


class ContextManager:
    """
    Seleziona i messaggi da inviare al modello AI.

    Questa prima versione mantiene solamente una finestra
    recente della conversazione, evitando che il contesto
    diventi troppo grande e rallenti il modello locale.
    """

    def __init__(self, max_messages: int = 12) -> None:
        if max_messages < 2:
            raise ValueError(
                "max_messages deve essere almeno 2."
            )

        self._max_messages = max_messages

    @property
    def max_messages(self) -> int:
        return self._max_messages

    def build_context(
        self,
        conversation_messages: list[Message],
    ) -> list[Message]:
        """
        Restituisce i messaggi più recenti da inviare al modello.

        Viene restituita una copia per evitare modifiche
        accidentali alla cronologia originale.
        """

        if not conversation_messages:
            return []

        recent_messages = conversation_messages[
            -self._max_messages:
        ]

        return deepcopy(recent_messages)