from collections.abc import Iterator


class StreamManager:
    """
    Gestisce lo streaming delle risposte AI.

    In futuro potrà inviare contemporaneamente
    il testo verso:
    - Console
    - Sintesi vocale
    - GUI
    - Dashboard Web
    """

    def __init__(self) -> None:
        self._buffer = ""

    def process(
        self,
        stream: Iterator[str],
    ) -> Iterator[str]:
        """
        Elabora lo stream proveniente dal provider AI.
        """

        self._buffer = ""

        for chunk in stream:

            if not chunk:
                continue

            self._buffer += chunk

            yield chunk

    @property
    def complete_response(self) -> str:
        """
        Restituisce l'intera risposta generata.
        """

        return self._buffer.strip()

    def clear(self) -> None:
        self._buffer = ""