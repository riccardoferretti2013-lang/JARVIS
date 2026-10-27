
from __future__ import annotations

from dataclasses import dataclass

from src.jarvis.agents.agent import Agent
from src.jarvis.agents.provider_router import (
    AgentProviderRouter,
)
from src.jarvis.agents.request_budget import (
    DailyRequestBudget,
)
from src.jarvis.ai.provider import Message


@dataclass(slots=True)
class AgentExecutionResult:
    agent_id: str
    agent_name: str
    task: str

    response: str
    success: bool

    provider_name: str = ""
    used_fallback: bool = False
    error: str | None = None


class AgentExecutor:
    """
    Esegue gli agenti della AI Company.

    Funzionalità:
    - Provider per singolo agente
    - Limite giornaliero API
    - Fallback su provider locale quando
      il budget API è esaurito
    - Gestione errori del provider
    - Recupero automatico delle risposte vuote
    - Diagnostica dettagliata
    """

    MAX_ATTEMPTS = 2

    def __init__(
        self,
        provider_router: AgentProviderRouter | None = None,
        request_budget: DailyRequestBudget | None = None,
    ) -> None:

        self._provider_router = (
            provider_router
            or AgentProviderRouter()
        )

        self._request_budget = (
            request_budget
            or DailyRequestBudget(
                daily_limit=50
            )
        )

    @property
    def provider_router(
        self,
    ) -> AgentProviderRouter:

        return self._provider_router

    @property
    def request_budget(
        self,
    ) -> DailyRequestBudget:

        return self._request_budget

    def execute(
        self,
        agent: Agent,
        task: str,
    ) -> AgentExecutionResult:

        clean_task = task.strip()

        # -----------------------------------------
        # VALIDAZIONE TASK
        # -----------------------------------------

        if not clean_task:

            return AgentExecutionResult(
                agent_id=agent.agent_id,
                agent_name=agent.name,
                task=task,
                response="",
                success=False,
                error="Il task è vuoto.",
            )

        # -----------------------------------------
        # CONTROLLO AGENTE
        # -----------------------------------------

        if not agent.enabled:

            return AgentExecutionResult(
                agent_id=agent.agent_id,
                agent_name=agent.name,
                task=clean_task,
                response="",
                success=False,
                error=(
                    f"L'agente {agent.name} "
                    "è disabilitato."
                ),
            )

        # -----------------------------------------
        # SELEZIONE PROVIDER
        # -----------------------------------------

        try:
            provider = (
                self._provider_router
                .get_provider_for_agent(agent)
            )

            provider_name = self._provider_name(
                provider
            )

        except Exception as exc:

            return self._failure(
                agent=agent,
                task=clean_task,
                provider_name="",
                used_fallback=False,
                error=(
                    "Errore selezione provider: "
                    f"{type(exc).__name__}: {exc}"
                ),
            )

        used_fallback = False

        # -----------------------------------------
        # BUDGET API GIORNALIERO
        # -----------------------------------------

        if self._is_metered_provider(
            provider_name
        ):

            try:
                allowed = (
                    self._request_budget
                    .consume(1)
                )

                if not allowed:

                    provider = (
                        self._provider_router
                        .get_local_provider_for_agent(
                            agent
                        )
                    )

                    provider_name = (
                        self._provider_name(
                            provider
                        )
                    )

                    used_fallback = True

            except Exception as exc:

                return self._failure(
                    agent=agent,
                    task=clean_task,
                    provider_name=provider_name,
                    used_fallback=used_fallback,
                    error=(
                        "Errore gestione budget: "
                        f"{type(exc).__name__}: {exc}"
                    ),
                )

        # -----------------------------------------
        # DISPONIBILITÀ PROVIDER
        # -----------------------------------------

        try:
            available = provider.is_available()

        except Exception as exc:

            return self._failure(
                agent=agent,
                task=clean_task,
                provider_name=provider_name,
                used_fallback=used_fallback,
                error=(
                    "Errore verifica provider: "
                    f"{type(exc).__name__}: {exc}"
                ),
            )

        if not available:

            return self._failure(
                agent=agent,
                task=clean_task,
                provider_name=provider_name,
                used_fallback=used_fallback,
                error=(
                    f"Il provider {provider_name} "
                    "non è disponibile."
                ),
            )

        # -----------------------------------------
        # COSTRUZIONE MESSAGGI
        # -----------------------------------------

        messages: list[Message] = [
            {
                "role": "system",
                "content": (
                    self._build_system_prompt(
                        agent
                    )
                ),
            },
            {
                "role": "user",
                "content": clean_task,
            },
        ]

        # -----------------------------------------
        # GENERAZIONE CON RETRY
        # -----------------------------------------

        clean_response = ""
        last_error = None
        attempts = 0

        for attempt in range(
            1,
            self.MAX_ATTEMPTS + 1,
        ):

            attempts = attempt

            # Ogni chiamata a un provider a consumo
            # successiva alla prima richiede budget.
            if (
                attempt > 1
                and self._is_metered_provider(
                    provider_name
                )
            ):

                try:
                    allowed = (
                        self._request_budget
                        .consume(1)
                    )

                except Exception as exc:

                    last_error = (
                        "Errore controllo budget retry: "
                        f"{type(exc).__name__}: {exc}"
                    )
                    break

                if not allowed:

                    last_error = (
                        "Budget API giornaliero "
                        "esaurito prima del retry."
                    )
                    break

            try:
                response = provider.generate(
                    messages
                )

                if isinstance(response, str):
                    clean_response = (
                        response.strip()
                    )
                else:
                    clean_response = ""

                if clean_response:
                    break

                last_error = (
                    "Il provider ha restituito "
                    "una risposta vuota "
                    f"(tentativo {attempt}/"
                    f"{self.MAX_ATTEMPTS}). "
                    f"Tipo risposta: "
                    f"{type(response).__name__}."
                )

            except Exception as exc:

                last_error = (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

        # -----------------------------------------
        # GESTIONE FALLIMENTO
        # -----------------------------------------

        if not clean_response:

            return self._failure(
                agent=agent,
                task=clean_task,
                provider_name=provider_name,
                used_fallback=used_fallback,
                error=(
                    f"L'agente {agent.name} "
                    "non ha prodotto una risposta "
                    f"valida dopo {attempts} "
                    "tentativo/i. "
                    f"Provider: {provider_name}. "
                    f"Ultimo errore: {last_error}"
                ),
            )

        # -----------------------------------------
        # RISULTATO POSITIVO
        # -----------------------------------------

        return AgentExecutionResult(
            agent_id=agent.agent_id,
            agent_name=agent.name,
            task=clean_task,
            response=clean_response,
            success=True,
            provider_name=provider_name,
            used_fallback=used_fallback,
        )

    # =============================================
    # METODI DI SUPPORTO
    # =============================================

    @staticmethod
    def _failure(
        agent: Agent,
        task: str,
        provider_name: str,
        used_fallback: bool,
        error: str,
    ) -> AgentExecutionResult:

        return AgentExecutionResult(
            agent_id=agent.agent_id,
            agent_name=agent.name,
            task=task,
            response="",
            success=False,
            provider_name=provider_name,
            used_fallback=used_fallback,
            error=error,
        )

    @staticmethod
    def _provider_name(
        provider,
    ) -> str:

        return str(
            getattr(
                provider,
                "provider_name",
                provider.__class__.__name__,
            )
        )

    @staticmethod
    def _is_metered_provider(
        provider_name: str,
    ) -> bool:

        return (
            provider_name.strip().lower()
            != "ollama"
        )

    @staticmethod
    def _build_system_prompt(
        agent: Agent,
    ) -> str:

        return (
            "Sei un agente specializzato della AI Company "
            "gestita da J.A.R.V.I.S.\n\n"

            f"Nome agente: {agent.name}\n"
            f"Ruolo: {agent.role}\n"
            f"Dipartimento: {agent.department}\n\n"

            "ISTRUZIONI SPECIFICHE:\n"
            f"{agent.system_prompt}\n\n"

            "REGOLE AZIENDALI:\n"
            "- J.A.R.V.I.S. è il manager principale.\n"
            "- Occupati esclusivamente del task assegnato.\n"
            "- Non inventare operazioni non eseguite.\n"
            "- Dichiara quando mancano informazioni.\n"
            "- Produci risultati concreti.\n"
            "- Mantieni la risposta focalizzata sul tuo ruolo.\n"
            "- Se il task riguarda la verifica di codice, "
            "fornisci risultati di analisi concreti.\n"
            "- Non dichiarare test eseguiti se non sono "
            "stati realmente eseguiti.\n"
            f"- Limite massimo indicativo: "
            f"{agent.max_tokens} token."
        )
