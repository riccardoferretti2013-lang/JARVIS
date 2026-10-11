from .embedding_service import EmbeddingService
from .semantic_repository import SemanticRepository
from .semantic_search_result import SemanticSearchResult
from .similarity import cosine_similarity
from ..memory import Memory
from ..memory_manager import MemoryManager


class SemanticSearchService:
    """
    Indicizza e ricerca i ricordi tramite embeddings.
    """

    def __init__(
        self,
        memory_manager: MemoryManager | None = None,
        embedding_service: EmbeddingService | None = None,
        semantic_repository: SemanticRepository | None = None,
    ) -> None:
        self._memory_manager = (
            memory_manager
            or MemoryManager()
        )

        self._embedding_service = (
            embedding_service
            or EmbeddingService()
        )

        self._semantic_repository = (
            semantic_repository
            or SemanticRepository()
        )

    @property
    def embedding_service(
        self,
    ) -> EmbeddingService:
        return self._embedding_service

    @property
    def repository(
        self,
    ) -> SemanticRepository:
        return self._semantic_repository

    def index_memory(
        self,
        memory: Memory,
    ) -> bool:
        if memory.memory_id is None:
            return False

        semantic_text = self._build_memory_text(
            memory
        )

        embedding = self._embedding_service.embed(
            semantic_text
        )

        if not embedding:
            return False

        self._semantic_repository.save(
            memory_id=memory.memory_id,
            text=semantic_text,
            embedding=embedding,
        )

        return True

    def index_missing(
        self,
    ) -> int:
        """
        Indicizza soltanto i ricordi che non hanno
        ancora un embedding salvato.
        """

        indexed_count = 0

        for memory in self._memory_manager.recall_all():
            if memory.memory_id is None:
                continue

            if self._semantic_repository.exists(
                memory.memory_id
            ):
                continue

            if self.index_memory(memory):
                indexed_count += 1

        return indexed_count

    def index_all(
        self,
    ) -> int:
        """
        Ricostruisce completamente l'indice semantico.
        """

        self._semantic_repository.clear()

        indexed_count = 0

        for memory in self._memory_manager.recall_all():
            if self.index_memory(memory):
                indexed_count += 1

        return indexed_count

    def search(
        self,
        query: str,
        limit: int = 10,
        minimum_similarity: float = 0.25,
    ) -> list[SemanticSearchResult]:
        clean_query = query.strip()

        if not clean_query:
            return []

        if limit < 1:
            return []

        query_embedding = (
            self._embedding_service.embed(
                clean_query
            )
        )

        if not query_embedding:
            return []

        results: list[SemanticSearchResult] = []

        for (
            memory_id,
            _,
            stored_embedding,
        ) in self._semantic_repository.get_all():
            similarity = cosine_similarity(
                query_embedding,
                stored_embedding,
            )

            if similarity < minimum_similarity:
                continue

            memory = (
                self._memory_manager.repository
                .get_by_id(memory_id)
            )

            if memory is None:
                self._semantic_repository.delete(
                    memory_id
                )
                continue

            results.append(
                SemanticSearchResult(
                    memory=memory,
                    similarity=similarity,
                )
            )

        results.sort(
            key=lambda result: result.similarity,
            reverse=True,
        )

        return results[:limit]

    def remove_memory(
        self,
        memory_id: int,
    ) -> bool:
        return self._semantic_repository.delete(
            memory_id
        )

    def clear(self) -> None:
        self._semantic_repository.clear()

    def count(self) -> int:
        return self._semantic_repository.count()

    @staticmethod
    def _build_memory_text(
        memory: Memory,
    ) -> str:
        return (
            f"Tipo di informazione: "
            f"{memory.memory_type.value}. "
            f"Argomento: {memory.key}. "
            f"Valore dell'utente: {memory.value}."
        )