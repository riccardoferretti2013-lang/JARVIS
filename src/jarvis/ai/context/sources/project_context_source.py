from ....projects import Project, ProjectManager

from .context_source import ContextSource


class ProjectContextSource(ContextSource):
    """
    Fornisce il progetto attivo al sistema AI.
    """

    def __init__(
        self,
        project_manager: ProjectManager,
    ) -> None:
        self._project_manager = project_manager

    @property
    def source_name(self) -> str:
        return "Project"

    def get_data(self) -> Project | None:
        return self._project_manager.get_active()