from ..providers import ContextProvider


class ContextProviderRegistry:
    """
    Registro di tutti i Context Provider.
    """

    def __init__(self) -> None:
        self._providers: list[ContextProvider] = []

    def register(
        self,
        provider: ContextProvider,
    ) -> None:
        if provider not in self._providers:
            self._providers.append(provider)

    def unregister(
        self,
        provider: ContextProvider,
    ) -> None:
        if provider in self._providers:
            self._providers.remove(provider)

    def clear(self) -> None:
        self._providers.clear()

    @property
    def providers(
        self,
    ) -> tuple[ContextProvider, ...]:
        return tuple(self._providers)