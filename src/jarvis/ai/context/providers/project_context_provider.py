from ..context_block import ContextBlock
from ..sources import ProjectContextSource
from .context_provider import ContextProvider


class ProjectContextProvider(ContextProvider):
    """
    Inserisce il progetto attivo nel contesto AI.
    """

    def __init__(
        self,
        source: ProjectContextSource,
    ) -> None:
        self._source = source

    @property
    def provider_name(self) -> str:
        return "Project"

    @property
    def priority(self) -> int:
        return 90

    def get_context(self) -> ContextBlock:
        project = self._source.get_data()

        if project is None:
            return ContextBlock(
                name=self.provider_name,
                priority=self.priority,
                messages=[],
            )

        description = (
            project.description
            or "Nessuna descrizione disponibile."
        )

        path = (
            project.path
            or "Nessun percorso configurato."
        )

        content = (
            "PROGETTO ATTIVO DELL'UTENTE:\n"
            f"- Nome: {project.name}\n"
            f"- Descrizione: {description}\n"
            f"- Percorso: {path}\n\n"
            "Le informazioni appartengono al progetto "
            "su cui sta lavorando l'utente."
        )

        return ContextBlock(
            name=self.provider_name,
            priority=self.priority,
            messages=[
                {
                    "role": "system",
                    "content": content,
                }
            ],
        )