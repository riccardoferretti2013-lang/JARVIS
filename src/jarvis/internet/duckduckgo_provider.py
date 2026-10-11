from urllib.parse import parse_qs, unquote, urlparse

import requests
from bs4 import BeautifulSoup

from .search_provider import SearchProvider
from .search_result import SearchResult


class DuckDuckGoProvider(SearchProvider):

    SEARCH_URL = (
        "https://html.duckduckgo.com/html/"
    )

    USER_AGENT = (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:

        clean_query = query.strip()

        if not clean_query:
            return []

        response = requests.post(
            self.SEARCH_URL,
            data={
                "q": clean_query,
            },
            headers={
                "User-Agent":
                    self.USER_AGENT,
            },
            timeout=10,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        results: list[
            SearchResult
        ] = []

        for result in soup.select(
            ".result"
        ):

            title_element = (
                result.select_one(
                    ".result__a"
                )
            )

            if title_element is None:
                continue

            title = (
                title_element
                .get_text(
                    " ",
                    strip=True,
                )
            )

            url = (
                title_element
                .get(
                    "href",
                    ""
                )
            )

            url = self._clean_url(
                url
            )

            snippet_element = (
                result.select_one(
                    ".result__snippet"
                )
            )

            snippet = ""

            if snippet_element is not None:

                snippet = (
                    snippet_element
                    .get_text(
                        " ",
                        strip=True,
                    )
                )

            if not title or not url:
                continue

            results.append(
                SearchResult(
                    title=title,
                    url=url,
                    snippet=snippet,
                )
            )

            if (
                len(results)
                >= max_results
            ):
                break

        return results

    @staticmethod
    def _clean_url(
        url: str,
    ) -> str:

        if not url:
            return ""

        if url.startswith(
            "//duckduckgo.com/l/"
        ):

            parsed = urlparse(
                "https:" + url
            )

            query = parse_qs(
                parsed.query
            )

            target = query.get(
                "uddg"
            )

            if target:
                return unquote(
                    target[0]
                )

        return url