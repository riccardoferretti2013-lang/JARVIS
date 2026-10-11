from collections import deque


class CommandHistory:
    """
    Gestisce la cronologia dei comandi della sessione.
    """

    def __init__(
        self,
        max_size: int = 100,
    ) -> None:
        if max_size < 1:
            raise ValueError(
                "max_size deve essere almeno 1."
            )

        self._commands: deque[str] = deque(
            maxlen=max_size
        )

    def add(
        self,
        command: str,
    ) -> None:
        clean_command = command.strip()

        if not clean_command:
            return

        self._commands.append(
            clean_command
        )

    def last(
        self,
        count: int = 10,
    ) -> list[str]:
        if count < 1:
            return []

        commands = list(
            self._commands
        )

        return commands[-count:]

    def get(
        self,
        position_from_end: int = 1,
    ) -> str | None:
        """
        Restituisce un comando contando dalla fine.

        1 = ultimo comando
        2 = penultimo comando
        3 = terzultimo comando
        """

        if position_from_end < 1:
            return None

        if position_from_end > len(self._commands):
            return None

        return list(self._commands)[
            -position_from_end
        ]

    def clear(self) -> None:
        self._commands.clear()

    def count(self) -> int:
        return len(self._commands)

    def is_empty(self) -> bool:
        return not self._commands