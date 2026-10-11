from .preferred_application import PreferredApplication
from .preferred_application_repository import (
    PreferredApplicationRepository,
)


class PreferredApplicationManager:
    """
    Gestisce la logica delle applicazioni preferite.
    """

    def __init__(
        self,
        repository: PreferredApplicationRepository | None = None,
    ) -> None:
        self._repository = (
            repository
            or PreferredApplicationRepository()
        )

    @property
    def repository(
        self,
    ) -> PreferredApplicationRepository:
        return self._repository

    def set_preferred(
        self,
        category: str,
        application_name: str,
        executable_path: str = "",
    ) -> PreferredApplication:
        application = PreferredApplication(
            category=category,
            application_name=application_name,
            executable_path=executable_path,
        )

        return self._repository.save(
            application
        )

    def get(
        self,
        category: str,
    ) -> PreferredApplication | None:
        return self._repository.get_by_category(
            category
        )

    def get_all(
        self,
    ) -> list[PreferredApplication]:
        return self._repository.get_all()

    def update_path(
        self,
        category: str,
        executable_path: str,
    ) -> PreferredApplication | None:
        return self._repository.update_path(
            category=category,
            executable_path=executable_path,
        )

    def delete(
        self,
        category: str,
    ) -> bool:
        return self._repository.delete(
            category
        )

    def count(self) -> int:
        return self._repository.count()