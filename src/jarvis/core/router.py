from collections.abc import Callable

from ..modules.system import SystemModule


CommandHandler = Callable[[], str]


class CommandRouter:
    """
    Gestisce esclusivamente i comandi locali di J.A.R.V.I.S.

    Se un comando non è locale, restituisce None.
    Sarà Assistant a inoltrarlo all'AIAgent.
    """

    def __init__(self) -> None:
        self.system_module = SystemModule()

        self.commands: dict[str, CommandHandler] = {
            "ciao": self._greet,
            "salve": self._greet,
            "buongiorno": self._greet,
            "come stai": self._how_are_you,
            "stato": self._get_status,
            "stato sistema": self._get_status,
            "che ore sono": self._get_time,
            "che ora è": self._get_time,
            "dimmi l'ora": self._get_time,
            "ora": self._get_time,
            "che data è": self._get_date,
            "che giorno è": self._get_date,
            "data": self._get_date,
        }

    def process(self, command: str) -> str | None:
        """
        Restituisce la risposta del comando locale.

        Se il comando non è registrato, restituisce None.
        """

        normalized_command = command.lower().strip()

        if not normalized_command:
            return None

        handler = self.commands.get(normalized_command)

        if handler is None:
            return None

        return handler()

    def _greet(self) -> str:
        return "Ciao. Come posso aiutarti?"

    def _how_are_you(self) -> str:
        return "Tutti i sistemi funzionano correttamente."

    def _get_status(self) -> str:
        return self.system_module.get_status()

    def _get_time(self) -> str:
        return self.system_module.get_time()

    def _get_date(self) -> str:
        return self.system_module.get_date()