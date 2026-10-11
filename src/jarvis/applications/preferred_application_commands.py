import re

from .preferred_application import PreferredApplication
from .preferred_application_manager import (
    PreferredApplicationManager,
)


class PreferredApplicationCommands:
    """
    Gestisce i comandi relativi
    alle applicazioni preferite.
    """

    def __init__(
        self,
        manager: PreferredApplicationManager | None = None,
    ) -> None:
        self._manager = (
            manager
            or PreferredApplicationManager()
        )

    @property
    def manager(
        self,
    ) -> PreferredApplicationManager:
        return self._manager

    def process(
        self,
        command: str,
    ) -> str | None:
        clean_command = command.strip()

        if not clean_command:
            return None

        processors = [
            self._process_set_preferred,
            self._process_set_path,
            self._process_details,
            self._process_delete,
        ]

        for processor in processors:
            response = processor(
                clean_command
            )

            if response is not None:
                return response

        lowered_command = clean_command.lower()

        if lowered_command in {
            "lista applicazioni preferite",
            "elenco applicazioni preferite",
            "mostra applicazioni preferite",
        }:
            return self._application_list_response()

        if lowered_command in {
            "numero applicazioni preferite",
            "quante applicazioni preferite",
            "conteggio applicazioni preferite",
        }:
            return self._application_count_response()

        return None

    def _process_set_preferred(
        self,
        command: str,
    ) -> str | None:
        match = re.fullmatch(
            (
                r"(?:imposta|usa|salva)\s+"
                r"(.+?)\s+come\s+"
                r"(.+?)\s+preferito"
            ),
            command,
            flags=re.IGNORECASE,
        )

        if match is None:
            match = re.fullmatch(
                (
                    r"il mio\s+"
                    r"(.+?)\s+preferito\s+è\s+"
                    r"(.+)"
                ),
                command,
                flags=re.IGNORECASE,
            )

            if match is None:
                return None

            category = self._clean_value(
                match.group(1)
            )

            application_name = self._clean_value(
                match.group(2)
            )

        else:
            application_name = self._clean_value(
                match.group(1)
            )

            category = self._clean_value(
                match.group(2)
            )

        application = self._manager.set_preferred(
            category=category,
            application_name=application_name,
        )

        return (
            f"{application.application_name} impostata "
            f"come applicazione preferita per "
            f"la categoria '{application.category}'."
        )

    def _process_set_path(
        self,
        command: str,
    ) -> str | None:
        match = re.fullmatch(
            (
                r"(?:percorso applicazione|"
                r"imposta percorso applicazione)\s+"
                r"(.+?)\s*:\s*(.+)"
            ),
            command,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        category = self._clean_value(
            match.group(1)
        )

        executable_path = self._clean_value(
            match.group(2)
        )

        application = self._manager.update_path(
            category=category,
            executable_path=executable_path,
        )

        if application is None:
            return (
                f"Non esiste un'applicazione preferita "
                f"per la categoria '{category}'."
            )

        return (
            f"Percorso di "
            f"'{application.application_name}' aggiornato."
        )

    def _process_details(
        self,
        command: str,
    ) -> str | None:
        match = re.fullmatch(
            (
                r"(?:applicazione preferita|"
                r"mostra applicazione preferita|"
                r"qual è la mia applicazione preferita per)\s+"
                r"(.+)"
            ),
            command,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        category = self._clean_value(
            match.group(1)
        )

        application = self._manager.get(
            category
        )

        if application is None:
            return (
                f"Non hai ancora impostato "
                f"un'applicazione preferita per "
                f"la categoria '{category}'."
            )

        return self._format_application(
            application
        )

    def _process_delete(
        self,
        command: str,
    ) -> str | None:
        match = re.fullmatch(
            (
                r"(?:elimina|cancella|rimuovi)\s+"
                r"applicazione preferita\s+(.+)"
            ),
            command,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        category = self._clean_value(
            match.group(1)
        )

        deleted = self._manager.delete(
            category
        )

        if not deleted:
            return (
                f"Non esiste un'applicazione preferita "
                f"per la categoria '{category}'."
            )

        return (
            f"Applicazione preferita per "
            f"la categoria '{category}' eliminata."
        )

    def _application_list_response(
        self,
    ) -> str:
        applications = self._manager.get_all()

        if not applications:
            return (
                "Non ci sono applicazioni preferite."
            )

        lines = [
            "Applicazioni preferite:"
        ]

        for application in applications:
            lines.append(
                f"• {application.category}: "
                f"{application.application_name}"
            )

        return "\n".join(lines)

    def _application_count_response(
        self,
    ) -> str:
        count = self._manager.count()

        if count == 0:
            return (
                "Non ci sono applicazioni preferite."
            )

        if count == 1:
            return (
                "C'è un'applicazione preferita salvata."
            )

        return (
            f"Ci sono {count} applicazioni "
            f"preferite salvate."
        )

    @staticmethod
    def _format_application(
        application: PreferredApplication,
    ) -> str:
        path = (
            application.executable_path
            or "non configurato"
        )

        return (
            f"Categoria: {application.category}\n"
            f"Applicazione: "
            f"{application.application_name}\n"
            f"Percorso: {path}"
        )

    @staticmethod
    def _clean_value(
        value: str,
    ) -> str:
        return (
            value
            .strip()
            .rstrip(".,!?")
        )