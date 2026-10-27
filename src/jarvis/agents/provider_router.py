from __future__ import annotations

from src.jarvis.agents.agent import Agent
from src.jarvis.ai.ollama_provider import OllamaProvider
from src.jarvis.ai.openai_provider import OpenAIProvider
from src.jarvis.ai.provider import AIProvider


class AgentProviderRouter:
    """
    Router dei provider AI della AI Company.

    Crea provider configurati sulle esigenze
    specifiche del singolo agente.

    Esempi:
    - Project Manager -> Ollama 64 token
    - QA Engineer -> Ollama 64 token
    - Backend Architect -> OpenAI 1024 token
    - Research Agent -> OpenAI 768 token
    """

    def __init__(self) -> None:

        self._providers: dict[
            str,
            AIProvider,
        ] = {}

        self._provider_cache: dict[
            tuple,
            AIProvider,
        ] = {}

        # Provider generici di base.
        self.register_provider(
            "ollama",
            OllamaProvider(
                max_tokens=64,
                timeout_seconds=30.0,
            ),
        )

        openai_provider = (
            OpenAIProvider(
                max_tokens=512,
                timeout_seconds=60.0,
            )
        )

        if openai_provider.is_available():

            self.register_provider(
                "api",
                openai_provider,
            )

            self.register_provider(
                "openai",
                openai_provider,
            )

    def register_provider(
        self,
        name: str,
        provider: AIProvider,
    ) -> None:

        clean_name = (
            name
            .strip()
            .lower()
        )

        if not clean_name:

            raise ValueError(
                "Il nome del provider "
                "non può essere vuoto."
            )

        self._providers[
            clean_name
        ] = provider

    def unregister_provider(
        self,
        name: str,
    ) -> None:

        clean_name = (
            name
            .strip()
            .lower()
        )

        self._providers.pop(
            clean_name,
            None,
        )

    def get_provider(
        self,
        name: str,
    ) -> AIProvider | None:

        clean_name = (
            name
            .strip()
            .lower()
        )

        return (
            self._providers
            .get(clean_name)
        )

    def has_provider(
        self,
        name: str,
    ) -> bool:

        clean_name = (
            name
            .strip()
            .lower()
        )

        return (
            clean_name
            in self._providers
        )

    def get_provider_for_agent(
        self,
        agent: Agent,
    ) -> AIProvider:

        provider_name = (
            agent.preferred_provider
            or "ollama"
        )

        clean_name = (
            provider_name
            .strip()
            .lower()
        )

        if clean_name == "ollama":

            return (
                self._get_ollama_for_agent(
                    agent
                )
            )

        if clean_name in {
            "api",
            "openai",
        }:

            if self.has_provider(
                "openai"
            ):

                return (
                    self._get_openai_for_agent(
                        agent
                    )
                )

            return (
                self._get_ollama_for_agent(
                    agent
                )
            )

        custom_provider = (
            self._providers
            .get(clean_name)
        )

        if custom_provider is not None:
            return custom_provider

        return (
            self._get_ollama_for_agent(
                agent
            )
        )

    def get_local_provider_for_agent(
        self,
        agent: Agent,
    ) -> AIProvider:
        """
        Crea un provider Ollama rispettando
        max_tokens e timeout dell'agente.

        Usato anche per i fallback.
        """

        return (
            self._get_ollama_for_agent(
                agent
            )
        )

    def is_provider_available(
        self,
        name: str,
    ) -> bool:

        provider = (
            self.get_provider(
                name
            )
        )

        if provider is None:
            return False

        try:

            return (
                provider
                .is_available()
            )

        except Exception:
            return False

    def get_registered_providers(
        self,
    ) -> list[str]:

        return sorted(
            self._providers.keys()
        )

    def _get_ollama_for_agent(
        self,
        agent: Agent,
    ) -> AIProvider:

        model = (
            agent.preferred_model
            or "qwen3:4b-instruct"
        )

        cache_key = (
            "ollama",
            model,
            agent.max_tokens,
            agent.timeout_seconds,
        )

        cached = (
            self._provider_cache
            .get(cache_key)
        )

        if cached is not None:
            return cached

        provider = OllamaProvider(
            model=model,
            max_tokens=agent.max_tokens,
            timeout_seconds=(
                agent.timeout_seconds
            ),
        )

        self._provider_cache[
            cache_key
        ] = provider

        return provider

    def _get_openai_for_agent(
        self,
        agent: Agent,
    ) -> AIProvider:

        model = (
            agent.preferred_model
            or None
        )

        cache_key = (
            "openai",
            model,
            agent.max_tokens,
            agent.timeout_seconds,
        )

        cached = (
            self._provider_cache
            .get(cache_key)
        )

        if cached is not None:
            return cached

        provider = OpenAIProvider(
            model=model,
            max_tokens=agent.max_tokens,
            timeout_seconds=(
                agent.timeout_seconds
            ),
        )

        self._provider_cache[
            cache_key
        ] = provider

        return provider