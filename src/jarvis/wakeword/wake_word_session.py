import time


class WakeWordSession:
    """
    Gestisce una sessione vocale temporaneamente attiva
    dopo il rilevamento della Wake Word.
    """

    def __init__(
        self,
        timeout_seconds: float = 8.0,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds deve essere maggiore di zero."
            )

        self._timeout_seconds = timeout_seconds
        self._active_until = 0.0

    @property
    def timeout_seconds(
        self,
    ) -> float:
        return self._timeout_seconds

    @property
    def is_active(
        self,
    ) -> bool:
        return time.monotonic() < self._active_until

    def activate(
        self,
    ) -> None:
        self._active_until = (
            time.monotonic()
            + self._timeout_seconds
        )

    def refresh(
        self,
    ) -> None:
        self.activate()

    def close(
        self,
    ) -> None:
        self._active_until = 0.0

    def remaining_seconds(
        self,
    ) -> float:
        remaining = (
            self._active_until
            - time.monotonic()
        )

        return max(
            0.0,
            remaining,
        )