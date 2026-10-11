from abc import ABC, abstractmethod

from .search_result import SearchResult


class SearchProvider(ABC):

    @abstractmethod
    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:
        raise NotImplementedError