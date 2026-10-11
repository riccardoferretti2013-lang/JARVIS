from .duckduckgo_provider import (
    DuckDuckGoProvider,
)
from .search_provider import (
    SearchProvider,
)
from .search_result import (
    SearchResult,
)


class InternetService:

    def __init__(
        self,
        search_provider: (
            SearchProvider | None
        ) = None,
    ) -> None:

        self._search_provider = (
            search_provider
            or DuckDuckGoProvider()
        )

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:

        clean_query = (
            query.strip()
        )

        if not clean_query:
            return []

        try:

            return (
                self._search_provider
                .search(
                    clean_query,
                    max_results=(
                        max_results
                    ),
                )
            )

        except Exception:
            return []

    @staticmethod
    def format_results_for_ai(
        results: list[
            SearchResult
        ],
    ) -> str:

        if not results:

            return (
                "Nessun risultato "
                "internet disponibile."
            )

        blocks: list[str] = []

        for index, result in enumerate(
            results,
            start=1,
        ):

            blocks.append(
                (
                    f"[RISULTATO {index}]\n"
                    f"Titolo: {result.title}\n"
                    f"URL: {result.url}\n"
                    f"Descrizione: "
                    f"{result.snippet}"
                )
            )

        return "\n\n".join(
            blocks
        )