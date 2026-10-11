from ....memory import Memory
from ....memory import MemoryService

from .context_source import ContextSource


class MemoryContextSource(ContextSource):
    """
    Fornisce i ricordi selezionati.
    """

    def __init__(
        self,
        memory_service: MemoryService,
    ) -> None:

        self._memory_service = (
            memory_service
        )

    @property
    def source_name(
        self,
    ) -> str:

        return "Memory"

    def get_data(
        self,
    ) -> list[Memory]:

        return (
            self._memory_service
            .get_selected_memories()
        )