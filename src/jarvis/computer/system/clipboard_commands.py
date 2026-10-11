from .clipboard_controller import ClipboardController


class ClipboardCommands:
    """
    Gestisce i comandi relativi
    agli appunti di Windows.
    """

    def __init__(
        self,
        controller: ClipboardController | None = None,
    ) -> None:
        self._controller = (
            controller
            or ClipboardController()
        )

    def process(
        self,
        command: str,
    ) -> str | None:
        clean_command = (
            command
            .strip()
        )

        if not clean_command:
            return None

        lower_command = (
            clean_command.lower()
        )

        if lower_command in {
            "appunti",
            "leggi appunti",
            "leggi gli appunti",
            "cosa c'è negli appunti",
            "cosa ce negli appunti",
            "mostra appunti",
            "mostra gli appunti",
        }:
            return self._read()

        if lower_command in {
            "svuota appunti",
            "svuota gli appunti",
            "cancella appunti",
            "cancella gli appunti",
        }:
            return self._clear()

        prefixes = (
            "copia negli appunti ",
            "copia negli appunti: ",
            "metti negli appunti ",
            "metti negli appunti: ",
        )

        for prefix in prefixes:
            if lower_command.startswith(
                prefix
            ):
                text = clean_command[
                    len(prefix):
                ].strip()

                return self._write(
                    text
                )

        return None

    def _read(
        self,
    ) -> str:
        text = (
            self._controller.get_text()
        )

        if not text:
            return (
                "Gli appunti sono vuoti."
            )

        return (
            "Negli appunti c'è: "
            f"{text}"
        )

    def _write(
        self,
        text: str,
    ) -> str:
        if not text:
            return (
                "Non hai indicato cosa copiare "
                "negli appunti."
            )

        if not self._controller.set_text(
            text
        ):
            return (
                "Non sono riuscito a copiare "
                "il testo negli appunti."
            )

        return (
            "Testo copiato negli appunti."
        )

    def _clear(
        self,
    ) -> str:
        self._controller.clear()

        return (
            "Appunti svuotati."
        )