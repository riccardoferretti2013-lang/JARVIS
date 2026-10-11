import re

from .project import Project
from .project_manager import ProjectManager


class ProjectCommands:
    """
    Gestisce i comandi relativi ai progetti.
    """

    def __init__(
        self,
        manager: ProjectManager | None = None,
    ) -> None:
        self._manager = (
            manager
            or ProjectManager()
        )

    @property
    def manager(self) -> ProjectManager:
        return self._manager

    def process(
        self,
        command: str,
    ) -> str | None:
        clean_command = command.strip()

        if not clean_command:
            return None

        response = self._process_create(
            clean_command
        )

        if response is not None:
            return response

        response = self._process_activate(
            clean_command
        )

        if response is not None:
            return response

        response = self._process_delete(
            clean_command
        )

        if response is not None:
            return response

        response = self._process_description(
            clean_command
        )

        if response is not None:
            return response

        response = self._process_path(
            clean_command
        )

        if response is not None:
            return response

        response = self._process_details(
            clean_command
        )

        if response is not None:
            return response

        lowered_command = clean_command.lower()

        if lowered_command == "progetto attivo":
            return self._active_project_response()

        if lowered_command in {
            "lista progetti",
            "elenco progetti",
            "mostra progetti",
        }:
            return self._project_list_response()

        if lowered_command in {
            "numero progetti",
            "quanti progetti",
            "conteggio progetti",
        }:
            return self._project_count_response()

        if lowered_command in {
            "disattiva progetto",
            "chiudi progetto",
            "nessun progetto attivo",
        }:
            return self._deactivate_project_response()

        return None

    def _process_create(
        self,
        command: str,
    ) -> str | None:
        match = re.fullmatch(
            r"crea progetto (.+)",
            command,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        name = self._clean_value(
            match.group(1)
        )

        if self._manager.exists(name):
            return (
                f"Il progetto '{name}' esiste già."
            )

        project = self._manager.create(
            name=name,
        )

        return (
            f"Progetto '{project.name}' creato."
        )

    def _process_activate(
        self,
        command: str,
    ) -> str | None:
        match = re.fullmatch(
            r"(?:apri|attiva|seleziona) progetto (.+)",
            command,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        name = self._clean_value(
            match.group(1)
        )

        project = self._manager.activate(
            name
        )

        if project is None:
            return (
                f"Il progetto '{name}' non esiste."
            )

        return (
            f"Progetto attivo: {project.name}"
        )

    def _process_delete(
        self,
        command: str,
    ) -> str | None:
        match = re.fullmatch(
            r"(?:elimina|cancella|rimuovi) progetto (.+)",
            command,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        name = self._clean_value(
            match.group(1)
        )

        deleted = self._manager.delete(
            name
        )

        if not deleted:
            return (
                f"Il progetto '{name}' non esiste."
            )

        return (
            f"Progetto '{name}' eliminato."
        )

    def _process_description(
        self,
        command: str,
    ) -> str | None:
        match = re.fullmatch(
            (
                r"(?:descrizione progetto|"
                r"imposta descrizione progetto)\s+"
                r"(.+?)\s*:\s*(.+)"
            ),
            command,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        name = self._clean_value(
            match.group(1)
        )

        description = self._clean_value(
            match.group(2)
        )

        project = self._manager.update_description(
            name=name,
            description=description,
        )

        if project is None:
            return (
                f"Il progetto '{name}' non esiste."
            )

        return (
            f"Descrizione del progetto "
            f"'{project.name}' aggiornata."
        )

    def _process_path(
        self,
        command: str,
    ) -> str | None:
        match = re.fullmatch(
            (
                r"(?:percorso progetto|"
                r"imposta percorso progetto)\s+"
                r"(.+?)\s*:\s*(.+)"
            ),
            command,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        name = self._clean_value(
            match.group(1)
        )

        path = self._clean_value(
            match.group(2)
        )

        project = self._manager.update_path(
            name=name,
            path=path,
        )

        if project is None:
            return (
                f"Il progetto '{name}' non esiste."
            )

        return (
            f"Percorso del progetto "
            f"'{project.name}' aggiornato."
        )

    def _process_details(
        self,
        command: str,
    ) -> str | None:
        match = re.fullmatch(
            (
                r"(?:dettagli progetto|"
                r"informazioni progetto|"
                r"mostra progetto)\s+(.+)"
            ),
            command,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        name = self._clean_value(
            match.group(1)
        )

        project = self._manager.get(
            name
        )

        if project is None:
            return (
                f"Il progetto '{name}' non esiste."
            )

        return self._format_project(
            project
        )

    def _active_project_response(self) -> str:
        project = self._manager.get_active()

        if project is None:
            return "Nessun progetto attivo."

        return self._format_project(
            project
        )

    def _project_list_response(self) -> str:
        projects = self._manager.get_all()

        if not projects:
            return "Non ci sono progetti."

        lines = [
            "Progetti disponibili:"
        ]

        for project in projects:
            marker = (
                "▶"
                if project.is_active
                else "•"
            )

            lines.append(
                f"{marker} {project.name}"
            )

        return "\n".join(lines)

    def _project_count_response(self) -> str:
        count = self._manager.count()

        if count == 0:
            return "Non ci sono progetti."

        if count == 1:
            return "C'è un progetto salvato."

        return (
            f"Ci sono {count} progetti salvati."
        )

    def _deactivate_project_response(self) -> str:
        deactivated = (
            self._manager.deactivate_all()
        )

        if not deactivated:
            return "Nessun progetto era attivo."

        return "Il progetto attivo è stato chiuso."

    @staticmethod
    def _format_project(
        project: Project,
    ) -> str:
        status = (
            "attivo"
            if project.is_active
            else "non attivo"
        )

        description = (
            project.description
            or "nessuna descrizione"
        )

        path = (
            project.path
            or "nessun percorso"
        )

        return (
            f"Progetto: {project.name}\n"
            f"Stato: {status}\n"
            f"Descrizione: {description}\n"
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