from .ollama_provider import OllamaProvider
from .provider import AIProvider


class ProviderManager:
    """
    Gestisce il provider AI attivo.
    """

    def __init__(self, provider: AIProvider | None = None) -> None:
        self._provider = provider or OllamaProvider()

    @property
    def provider(self) -> AIProvider:
        return self._provider

    def set_provider(self, provider: AIProvider) -> None:
        if not isinstance(provider, AIProvider):
            raise TypeError(
                "Il provider deve implementare l'interfaccia AIProvider."
            )

        self._provider = provider

    def is_available(self) -> bool:
        return self._provider.is_available()

    def get_provider_info(self) -> str:
        return (
            f"{self._provider.provider_name} "
            f"({self._provider.model_name})"
        )