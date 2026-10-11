from .shutdown_controller import ShutdownController


class ShutdownCommands:
    """
    Gestisce i comandi di spegnimento
    con conferma obbligatoria.
    """

    def __init__(
        self,
        controller: ShutdownController | None = None,
    ) -> None:
        self._controller = (
            controller
            or ShutdownController()
        )

        self._confirmation_pending = False

    @property
    def confirmation_pending(
        self,
    ) -> bool:
        return self._confirmation_pending

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
            "spegni",
            "spegni pc",
            "spegni il pc",
            "spegni computer",
            "spegni il computer",
            "spegni windows",
        }:
            self._confirmation_pending = True

            return (
                "Confermi lo spegnimento del computer? "
                'Di\' "conferma spegnimento" oppure "annulla".'
            )

        if clean_command in {
            "conferma spegnimento",
            "confermo spegnimento",
            "si spegni",
            "sì spegni",
        }:
            if not self._confirmation_pending:
                return (
                    "Non c'è nessuno spegnimento "
                    "in attesa di conferma."
                )

            self._confirmation_pending = False

            if not self._controller.shutdown(
                delay_seconds=10
            ):
                return (
                    "Non sono riuscito ad avviare "
                    "lo spegnimento del computer."
                )

            return (
                "Spegnimento del computer programmato "
                "tra 10 secondi."
            )

        if clean_command == "annulla":
            if not self._confirmation_pending:
                return None

            self._confirmation_pending = False

            return "Spegnimento annullato."

        if clean_command in {
            "annulla spegnimento",
            "non spegnere",
        }:
            if self._confirmation_pending:
                self._confirmation_pending = False

                return "Spegnimento annullato."

            if self._controller.cancel():
                return (
                    "Spegnimento programmato annullato."
                )

            return (
                "Non c'è nessuno spegnimento "
                "da annullare."
            )

        return None