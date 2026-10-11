from .memory import Memory, MemoryType
from .memory_repository import MemoryRepository


class MemoryManager:
    """
    Gestisce la memoria permanente di J.A.R.V.I.S.
    """

    def __init__(
        self,
        repository: MemoryRepository | None = None,
    ) -> None:

        self._repository = (
            repository
            or MemoryRepository()
        )

    @property
    def repository(
        self,
    ) -> MemoryRepository:
        return self._repository

    def remember(
        self,
        memory: Memory,
    ) -> Memory:
        """
        Salva un ricordo.
        """

        return self._repository.save(
            memory
        )

    def recall(
        self,
        key: str,
        memory_type: MemoryType | None = None,
    ) -> list[Memory]:
        """
        Cerca un ricordo.
        """

        return self._repository.get_by_key(
            key,
            memory_type,
        )

    def recall_all(
        self,
    ) -> list[Memory]:
        """
        Restituisce tutti i ricordi.
        """

        return self._repository.get_all()

    def forget(
        self,
        memory_id: int,
    ) -> bool:
        """
        Elimina un ricordo.
        """

        return self._repository.delete(
            memory_id
        )

    def clear(self) -> None:
        """
        Cancella tutta la memoria.
        """

        self._repository.clear()

    def count(self) -> int:
        return self._repository.count()