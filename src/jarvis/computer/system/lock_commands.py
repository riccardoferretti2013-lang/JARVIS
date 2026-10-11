from .lock_controller import LockController


class LockCommands:
    """
    Gestisce i comandi relativi
    al blocco del computer.
    """

    def __init__(
        self,
        controller: LockController | None = None,
    ) -> None:
        self._controller = (
            controller
            or LockController()
        )

    def process(
        self,
        command: str,
    ) -> str | None:
        clean_command = (
            command
            .strip()
            .lower()
        )

        if not clean_command:
            return None

        if clean_command in {
            "blocca pc",
            "blocca il pc",
            "blocca computer",
            "blocca il computer",
            "blocca windows",
            "blocca la sessione",
        }:
            return self._lock()

        return None

    def _lock(
        self,
    ) -> str:
        if not self._controller.lock():
            return (
                "Non sono riuscito a bloccare "
                "il computer."
            )

        return "Computer bloccato."