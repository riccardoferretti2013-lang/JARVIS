from __future__ import annotations

from dataclasses import dataclass

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

    @property
    def success(self) -> bool:

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

            return CompanyExecutionResult(
                mode="workflow",
                decision=decision,
                workflow_result=(
                    workflow_result
                ),
            )

        if event_callback is not None:
            event_callback({"event": "single_started", "message": "Esecuzione agente singolo"})
        single_result = (
            self.execute_task(
                task
            )
        )

        return CompanyExecutionResult(
            mode="single",
            decision=decision,
            single_result=(
                single_result
            ),
        )

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