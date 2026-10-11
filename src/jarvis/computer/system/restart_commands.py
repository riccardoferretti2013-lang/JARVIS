from .restart_controller import RestartController


class RestartCommands:
    """
    Gestisce i comandi di riavvio
    con conferma obbligatoria.
    """

    def __init__(
        self,
        controller: RestartController | None = None,
    ) -> None:
        self._controller = (
            controller
            or RestartController()
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
            "riavvia",
            "riavvia pc",
            "riavvia il pc",
            "riavvia computer",
            "riavvia il computer",
            "riavvia windows",
        }:
            self._confirmation_pending = True

            return (
                "Confermi il riavvio del computer? "
                'Di\' "conferma riavvio" oppure "annulla".'
            )

        if clean_command in {
            "conferma riavvio",
            "confermo riavvio",
            "si riavvia",
            "sì riavvia",
        }:
            if not self._confirmation_pending:
                return (
                    "Non c'è nessun riavvio "
                    "in attesa di conferma."
                )

            self._confirmation_pending = False

            if not self._controller.restart(
                delay_seconds=10
            ):
                return (
                    "Non sono riuscito ad avviare "
                    "il riavvio del computer."
                )

            return (
                "Riavvio del computer programmato "
                "tra 10 secondi."
            )

        if clean_command == "annulla":
            if not self._confirmation_pending:
                return None

            self._confirmation_pending = False

            return "Riavvio annullato."

        if clean_command in {
            "annulla riavvio",
            "non riavviare",
        }:
            if self._confirmation_pending:
                self._confirmation_pending = False

                return "Riavvio annullato."

            if self._controller.cancel():
                return (
                    "Riavvio programmato annullato."
                )

            return (
                "Non c'è nessun riavvio "
                "da annullare."
            )

        return None