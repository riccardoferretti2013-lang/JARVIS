from __future__ import annotations

from dataclasses import dataclass

from src.jarvis.agents.agent import Agent
from src.jarvis.agents.agent_executor import (
    AgentExecutionResult,
    AgentExecutor,
)
from src.jarvis.agents.agent_registry import AgentRegistry
from src.jarvis.agents.agent_selector import (
    AgentSelection,
    AgentSelector,
)


@dataclass(slots=True)
class AgentRouteResult:
    """
    Risultato completo del routing di un task verso un agente.
    """

    task: str
    selection: AgentSelection
    execution: AgentExecutionResult | None

    @property
    def agent(self) -> Agent | None:
        return self.selection.agent

    @property
    def success(self) -> bool:
        return (
            self.execution is not None
            and self.execution.success
        )

    @property
    def response(self) -> str:
        if self.execution is None:
            return ""

        return self.execution.response

    @property
    def error(self) -> str | None:
        if self.execution is None:
            return "Nessuna esecuzione effettuata."

        return self.execution.error


class AgentRouter:
    """
    Coordina selezione ed esecuzione degli agenti.

    Flusso:

    task
      ↓
    AgentSelector
      ↓
    agente specializzato
      ↓
    AgentExecutor
      ↓
    provider AI
      ↓
    risposta
    """

    def __init__(
        self,
        registry: AgentRegistry,
        selector: AgentSelector | None = None,
        executor: AgentExecutor | None = None,
    ) -> None:
        self._registry = registry

        self._selector = (
            selector
            or AgentSelector(registry)
        )

        self._executor = (
            executor
            or AgentExecutor()
        )

    @property
    def registry(self) -> AgentRegistry:
        return self._registry

    @property
    def selector(self) -> AgentSelector:
        return self._selector

    @property
    def executor(self) -> AgentExecutor:
        return self._executor

    def route(
        self,
        task: str,
    ) -> AgentRouteResult:
        """
        Seleziona automaticamente un agente ed esegue il task.
        """

        clean_task = task.strip()

        if not clean_task:
            return AgentRouteResult(
                task=task,
                selection=AgentSelection(
                    agent=None,
                    score=0,
                    reason="Task vuoto.",
                ),
                execution=None,
            )

        selection = (
            self._selector
            .select_or_default(clean_task)
        )

        if selection.agent is None:
            return AgentRouteResult(
                task=clean_task,
                selection=selection,
                execution=None,
            )

        execution = (
            self._executor
            .execute(
                agent=selection.agent,
                task=clean_task,
            )
        )

        return AgentRouteResult(
            task=clean_task,
            selection=selection,
            execution=execution,
        )