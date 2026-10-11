from .memory import Memory
from .memory_extractor import MemoryExtractor
from .memory_manager import MemoryManager
from .selectors import MemorySelector
from .semantic import SemanticSearchService


class MemoryService:
    """
    Gestisce la memoria permanente e
    la ricerca semantica di J.A.R.V.I.S.
    """

    def __init__(
        self,
        memory_manager: MemoryManager | None = None,
        memory_extractor: MemoryExtractor | None = None,
        memory_selector: MemorySelector | None = None,
        semantic_search: SemanticSearchService | None = None,
    ) -> None:
        self._manager = (
            memory_manager
            or MemoryManager()
        )

        self._extractor = (
            memory_extractor
            or MemoryExtractor()
        )

        self._selector = (
            memory_selector
            or MemorySelector()
        )

        self._semantic_search = (
            semantic_search
            or SemanticSearchService(
                memory_manager=self._manager
            )
        )

        self._current_query = ""
        self._semantic_index_checked = False

    @property
    def manager(self) -> MemoryManager:
        return self._manager

    @property
    def extractor(self) -> MemoryExtractor:
        return self._extractor

    @property
    def selector(self) -> MemorySelector:
        return self._selector

    @property
    def semantic_search(
        self,
    ) -> SemanticSearchService:
        return self._semantic_search

    def process_user_message(
        self,
        message: str,
    ) -> list[Memory]:
        clean_message = message.strip()

        if not clean_message:
            return []

        self._current_query = clean_message

        extracted_memories = self._extractor.extract(
            clean_message
        )

        saved_memories: list[Memory] = []

        for memory in extracted_memories:
            saved_memory = self._manager.remember(
                memory
            )

            saved_memories.append(
                saved_memory
            )

            try:
                self._semantic_search.index_memory(
                    saved_memory
                )

            except RuntimeError:
                pass

        return saved_memories

    def get_all_memories(
        self,
    ) -> list[Memory]:
        return self._manager.recall_all()

    def get_selected_memories(
        self,
        limit: int = 20,
    ) -> list[Memory]:
        """
        Recupera prima i ricordi semanticamente pertinenti
        e completa il risultato con quelli più importanti.
        """

        if limit < 1:
            return []

        self._ensure_semantic_index()

        selected: list[Memory] = []
        selected_ids: set[int] = set()

        if self._current_query:
            try:
                semantic_results = (
                    self._semantic_search.search(
                        query=self._current_query,
                        limit=limit,
                        minimum_similarity=0.25,
                    )
                )

                for result in semantic_results:
                    memory = result.memory

                    selected.append(memory)

                    if memory.memory_id is not None:
                        selected_ids.add(
                            memory.memory_id
                        )

            except RuntimeError:
                pass

        fallback_memories = self._selector.select(
            self.get_all_memories()
        )

        for memory in fallback_memories:
            if len(selected) >= limit:
                break

            if (
                memory.memory_id is not None
                and memory.memory_id in selected_ids
            ):
                continue

            selected.append(memory)

            if memory.memory_id is not None:
                selected_ids.add(
                    memory.memory_id
                )

        return selected[:limit]

    def rebuild_semantic_index(
        self,
    ) -> int:
        indexed_count = (
            self._semantic_search.index_all()
        )

        self._semantic_index_checked = True

        return indexed_count

    def forget(
        self,
        memory_id: int,
    ) -> bool:
        deleted = self._manager.forget(
            memory_id
        )

        if deleted:
            self._semantic_search.remove_memory(
                memory_id
            )

        return deleted

    def clear(self) -> None:
        self._manager.clear()
        self._semantic_search.clear()

        self._current_query = ""
        self._semantic_index_checked = True

    def count(self) -> int:
        return self._manager.count()

    def semantic_count(self) -> int:
        return self._semantic_search.count()

    def _ensure_semantic_index(self) -> None:
        if self._semantic_index_checked:
            return

        try:
            self._semantic_search.index_missing()

        except RuntimeError:
            return

        self._semantic_index_checked = True