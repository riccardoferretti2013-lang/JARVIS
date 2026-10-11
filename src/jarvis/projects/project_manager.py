from .project import Project
from .project_repository import ProjectRepository


class ProjectManager:
    """
    Gestisce la logica dei progetti.
    """

    def __init__(
        self,
        repository: ProjectRepository | None = None,
    ) -> None:

        self._repository = (
            repository
            or ProjectRepository()
        )

    @property
    def repository(
        self,
    ) -> ProjectRepository:
        return self._repository

    def create(
        self,
        name: str,
        description: str = "",
        path: str = "",
        make_active: bool = False,
    ) -> Project:

        project = Project(
            name=name,
            description=description,
            path=path,
            is_active=make_active,
        )

        return self._repository.save(
            project
        )

    def exists(
        self,
        name: str,
    ) -> bool:

        return (
            self._repository.get_by_name(
                name
            )
            is not None
        )

    def get(
        self,
        name: str,
    ) -> Project | None:

        return self._repository.get_by_name(
            name
        )

    def get_active(
        self,
    ) -> Project | None:

        return self._repository.get_active()

    def get_all(
        self,
    ) -> list[Project]:

        return self._repository.get_all()

    def count(
        self,
    ) -> int:

        return self._repository.count()

    def activate(
        self,
        name: str,
    ) -> Project | None:

        return self._repository.set_active(
            name
        )

    def deactivate_all(
        self,
    ) -> bool:

        return self._repository.clear_active()

    def update_description(
        self,
        name: str,
        description: str,
    ) -> Project | None:

        return (
            self._repository.update_description(
                name,
                description,
            )
        )

    def update_path(
        self,
        name: str,
        path: str,
    ) -> Project | None:

        return (
            self._repository.update_path(
                name,
                path,
            )
        )

    def delete(
        self,
        name: str,
    ) -> bool:

        return self._repository.delete(
            name
        )