from __future__ import annotations

from dataclasses import dataclass, replace

from src.jarvis.agents.agent import Agent
from src.jarvis.agents.agent_registry import AgentRegistry
from src.jarvis.agents.agent_router import (
    AgentRouteResult,
    AgentRouter,
)
from src.jarvis.agents.default_agents import (
    create_default_agents,
)
from src.jarvis.agents.execution_decider import (
    ExecutionDecision,
    ExecutionDecider,
)
from src.jarvis.agents.task_planner import TaskPlan
from src.jarvis.agents.workflow_manager import (
    WorkflowManager,
    WorkflowResult,
)


@dataclass(slots=True)
class CompanyStatus:
    total_agents: int
    enabled_agents: int
    disabled_agents: int
    departments: list[str]


@dataclass(slots=True)
class CompanyExecutionResult:
    mode: str
    decision: ExecutionDecision

    single_result: AgentRouteResult | None = None
    workflow_result: WorkflowResult | None = None
    final_response: str = ""
    final_success: bool | None = None

    @property
    def success(self) -> bool:

        if self.final_success is not None:
            return self.final_success

        if self.mode == "single":

            if self.single_result is None:
                return False

            return self.single_result.success

        if self.workflow_result is None:
            return False

        return self.workflow_result.success


class CompanyManager:
    """
    Manager centrale della AI Company.

    Può:
    - usare un singolo agente;
    - usare un workflow;
    - decidere automaticamente quale modalità usare.
    """

    def __init__(
        self,
        registry: AgentRegistry | None = None,
        router: AgentRouter | None = None,
        workflow_manager: WorkflowManager | None = None,
        execution_decider: ExecutionDecider | None = None,
    ) -> None:

        self._registry = (
            registry
            or AgentRegistry()
        )

        if self._registry.count() == 0:

            self._registry.register_many(
                create_default_agents()
            )

        self._router = (
            router
            or AgentRouter(
                self._registry
            )
        )

        self._workflow_manager = (
            workflow_manager
            or WorkflowManager(
                registry=self._registry,
                max_api_requests=5,
            )
        )

        self._execution_decider = (
            execution_decider
            or ExecutionDecider()
        )

    @property
    def registry(self) -> AgentRegistry:
        return self._registry

    @property
    def router(self) -> AgentRouter:
        return self._router

    @property
    def workflow_manager(
        self,
    ) -> WorkflowManager:
        return self._workflow_manager

    @property
    def execution_decider(
        self,
    ) -> ExecutionDecider:
        return self._execution_decider

    def execute_task(
        self,
        task: str,
    ) -> AgentRouteResult:

        return (
            self._router
            .route(task)
        )

    def execute_workflow(
        self,
        task: str,
        event_callback=None,
    ) -> WorkflowResult:

        return (
            self._workflow_manager
            .execute(task, event_callback=event_callback)
        )

    def execute_auto(
        self,
        task: str,
        event_callback=None,
    ) -> CompanyExecutionResult:
        """
        J.A.R.V.I.S. decide automaticamente
        se usare un singolo agente oppure
        un workflow multi-agent.
        """

        decision = (
            self._execution_decider
            .decide(task)
        )

        if decision.use_workflow:

            workflow_result = (
                self.execute_workflow(
                    task,
                    event_callback=event_callback,
                )
            )

            final_text, final_ok = self._integrate_as_ceo(task, workflow_result, event_callback)
            return CompanyExecutionResult(
                mode="workflow",
                decision=decision,
                workflow_result=workflow_result,
                final_response=final_text,
                final_success=final_ok,
            )

        if event_callback is not None:
            event_callback({"event": "single_started", "message": "Esecuzione agente singolo"})
        single_result = (
            self.execute_task(
                task
            )
        )

        final_text, final_ok = self._integrate_as_ceo(task, single_result, event_callback)
        return CompanyExecutionResult(
            mode="single",
            decision=decision,
            single_result=single_result,
            final_response=final_text,
            final_success=final_ok,
        )

    def _integrate_as_ceo(self, task, source_result, event_callback=None):
        # Il CEO integra i contributi degli agenti.
        def emit(event, **data):
            if event_callback is not None:
                event_callback({"event": event, **data})

        if hasattr(source_result, "steps"):
            contributions = [
                f"AGENTE {s.agent_name} (successo={s.success}):\n{s.response}"
                for s in source_result.steps if s.response
            ]
        else:
            response = getattr(source_result, "response", "") or ""
            contributions = [f"AGENTE ESECUTORE:\n{response}"] if response else []
        if not contributions:
            emit("ceo_error", message="Nessun contributo da integrare")
            return "Nessun contributo utile prodotto dagli agenti.", False

        ceo = next((a for a in self._registry.enabled()
                    if "jarvis" in a.name.lower().replace(".", "") or
                    "j.a.r.v.i.s" in a.name.lower()), None)
        if ceo is None:
            emit("ceo_error", message="Agente CEO J.A.R.V.I.S. non trovato")
            return "CEO J.A.R.V.I.S. non disponibile: nessun file consegnato.", False

        emit("ceo_started", agent_id=str(ceo.agent_id), message="Integrazione finale in corso")
        context = "\n\n".join(contributions)
        # Evita di passare al modello un contesto illimitato.
        context = context[-18000:]
        instruction = (
            "Sei J.A.R.V.I.S., CEO e integratore finale della AI Company.\n"
            "MISSIONE ORIGINALE:\n" + task + "\n\n"
            "CONTRIBUTI DEGLI AGENTI:\n" + context + "\n\n"
            "Crea un PROGRAMMA DEFINITIVO, completo e coerente, non una spiegazione. "
            "Se il compito richiede una GUI, implementala realmente con PySide6. "
            "Rispondi con UN SOLO blocco Markdown ```python seguito dal codice COMPLETO "
            "di main.py e chiuso da ```. Non usare segnaposto, omissioni o puntini. "
            "Includi tutti gli import e l'entry point if __name__ == '__main__'. "
            "Se non puoi produrre un file completo, spiega l'impossibilita senza inventare codice."
        )
        try:
            # Mantiene il provider configurato per il CEO, aumentando il budget
            # di output per ridurre il rischio di troncamento.
            ceo_for_execution = replace(ceo, max_tokens=max(4096, ceo.max_tokens))
            result = self._workflow_manager.executor.execute(
                agent=ceo_for_execution, task=instruction
            )
            text = getattr(result, "response", "") or ""
            ok = bool(getattr(result, "success", False)) and bool(text.strip())
            emit("ceo_completed", agent_id=str(ceo.agent_id), success=ok,
                 message=(text[:250] if ok else (getattr(result, "error", "") or "CEO senza risposta")))
            return text, ok
        except Exception as exc:
            emit("ceo_error", message=str(exc))
            return f"Integrazione CEO fallita: {exc}", False

    def preview_workflow(
        self,
        task: str,
    ) -> TaskPlan:

        return (
            self._workflow_manager
            .preview(task)
        )

    def preview_execution(
        self,
        task: str,
    ) -> ExecutionDecision:
        """
        Decide la modalità senza eseguire AI.
        """

        return (
            self._execution_decider
            .decide(task)
        )

    def get_agent(
        self,
        agent_id: str,
    ) -> Agent | None:

        return (
            self._registry
            .get(agent_id)
        )

    def get_agents(
        self,
        enabled_only: bool = False,
    ) -> list[Agent]:

        if enabled_only:

            return (
                self._registry
                .enabled()
            )

        return (
            self._registry
            .all()
        )

    def enable_agent(
        self,
        agent_id: str,
    ) -> bool:

        return (
            self._registry
            .enable(agent_id)
        )

    def disable_agent(
        self,
        agent_id: str,
    ) -> bool:

        return (
            self._registry
            .disable(agent_id)
        )

    def get_departments(
        self,
    ) -> list[str]:

        departments = {
            agent.department
            for agent in self._registry.all()
        }

        return sorted(
            departments
        )

    def get_department_agents(
        self,
        department: str,
    ) -> list[Agent]:

        return (
            self._registry
            .by_department(
                department
            )
        )

    def get_status(
        self,
    ) -> CompanyStatus:

        total = (
            self._registry
            .count()
        )

        enabled = (
            self._registry
            .count_enabled()
        )

        return CompanyStatus(
            total_agents=total,
            enabled_agents=enabled,
            disabled_agents=(
                total - enabled
            ),
            departments=(
                self.get_departments()
            ),
        )

    def print_status(
        self,
    ) -> None:

        status = (
            self.get_status()
        )

        print()
        print(
            "J.A.R.V.I.S. AI COMPANY"
        )
        print(
            "----------------------"
        )
        print(
            "Agenti totali:",
            status.total_agents,
        )
        print(
            "Agenti attivi:",
            status.enabled_agents,
        )
        print(
            "Agenti disabilitati:",
            status.disabled_agents,
        )
        print(
            "Dipartimenti:",
            ", ".join(
                status.departments
            ),
        )
        print()