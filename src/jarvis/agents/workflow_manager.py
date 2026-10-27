from __future__ import annotations

from dataclasses import dataclass, field, replace

from src.jarvis.agents.agent import Agent
from src.jarvis.agents.agent_executor import (
    AgentExecutionResult,
    AgentExecutor,
)
from src.jarvis.agents.agent_registry import AgentRegistry
from src.jarvis.agents.task_planner import (
    PlannedTask,
    TaskPlan,
    TaskPlanner,
)


@dataclass(slots=True)
class WorkflowStepResult:
    """
    Risultato di un singolo step del workflow.
    """

    task_id: int
    agent_id: str
    agent_name: str

    success: bool

    provider_name: str

    response: str

    used_local_fallback: bool = False

    error: str | None = None


@dataclass(slots=True)
class WorkflowResult:
    """
    Risultato completo di un workflow multi-agent.
    """

    original_task: str

    plan: TaskPlan

    steps: list[WorkflowStepResult] = field(
        default_factory=list
    )

    api_requests_used: int = 0

    max_api_requests: int = 2

    @property
    def success(self) -> bool:

        if not self.steps:
            return False

        return all(
            step.success
            for step in self.steps
        )

    @property
    def completed_steps(self) -> int:

        return sum(
            1
            for step in self.steps
            if step.success
        )

    @property
    def failed_steps(self) -> int:

        return sum(
            1
            for step in self.steps
            if not step.success
        )


class WorkflowManager:
    """
    Gestisce workflow multi-agent della AI Company.

    Funzioni:
    - crea il piano;
    - esegue gli agenti in sequenza;
    - passa contesto tra gli agenti;
    - limita il numero di chiamate API;
    - usa Ollama quando il limite del workflow è raggiunto.

    Limite predefinito:
        massimo 2 chiamate API per workflow.
    """

    def __init__(
        self,
        registry: AgentRegistry,
        planner: TaskPlanner | None = None,
        executor: AgentExecutor | None = None,
        max_api_requests: int = 2,
        max_context_characters: int = 2500,
    ) -> None:

        if max_api_requests < 0:
            raise ValueError(
                "max_api_requests non può essere negativo."
            )

        if max_context_characters < 500:
            raise ValueError(
                "max_context_characters deve essere almeno 500."
            )

        self._registry = registry

        self._planner = (
            planner
            or TaskPlanner(
                registry
            )
        )

        self._executor = (
            executor
            or AgentExecutor()
        )

        self._max_api_requests = (
            max_api_requests
        )

        self._max_context_characters = (
            max_context_characters
        )

    @property
    def planner(self) -> TaskPlanner:
        return self._planner

    @property
    def executor(self) -> AgentExecutor:
        return self._executor

    @property
    def max_api_requests(self) -> int:
        return self._max_api_requests

    def create_plan(
        self,
        task: str,
    ) -> TaskPlan:

        return (
            self._planner
            .create_plan(task)
        )

    def execute(
        self,
        task: str,
        event_callback=None,
    ) -> WorkflowResult:

        plan = (
            self.create_plan(
                task
            )
        )

        if event_callback is not None:
            event_callback({"event": "plan_created", "total": len(plan.tasks)})

        workflow = WorkflowResult(
            original_task=task.strip(),
            plan=plan,
            max_api_requests=(
                self._max_api_requests
            ),
        )

        if plan.is_empty():
            return workflow

        previous_results: list[
            WorkflowStepResult
        ] = []

        for planned_task in plan.tasks:

            if event_callback is not None:
                event_callback({"event": "agent_started", "agent_id": planned_task.agent_id, "task_id": planned_task.task_id})

            agent = (
                self._registry
                .get(
                    planned_task.agent_id
                )
            )

            if agent is None:

                step = WorkflowStepResult(
                    task_id=planned_task.task_id,
                    agent_id=planned_task.agent_id,
                    agent_name="UNKNOWN",
                    success=False,
                    provider_name="",
                    response="",
                    error=(
                        "Agente non trovato "
                        "nel registry."
                    ),
                )

                workflow.steps.append(
                    step
                )
                if event_callback is not None:
                    event_callback({"event": "agent_completed", "agent_id": step.agent_id, "task_id": step.task_id, "success": False, "message": step.error or ""})

                continue

            execution_agent = agent

            used_local_fallback = False

            if self._requires_api(
                agent
            ):

                if (
                    workflow.api_requests_used
                    >= self._max_api_requests
                ):

                    execution_agent = (
                        self._create_local_fallback_agent(
                            agent
                        )
                    )

                    used_local_fallback = True

                else:

                    workflow.api_requests_used += 1

            instruction = (
                self._build_instruction_with_context(
                    planned_task=planned_task,
                    previous_results=previous_results,
                )
            )

            result = (
                self._executor
                .execute(
                    agent=execution_agent,
                    task=instruction,
                )
            )

            step = (
                self._convert_result(
                    planned_task=planned_task,
                    agent=agent,
                    execution=result,
                    used_local_fallback=(
                        used_local_fallback
                    ),
                )
            )

            workflow.steps.append(
                step
            )
            if event_callback is not None:
                event_callback({"event": "agent_completed", "agent_id": step.agent_id, "task_id": step.task_id, "success": step.success, "message": (step.error or step.response)[:250]})

            previous_results.append(
                step
            )

            planned_task.completed = (
                step.success
            )

            planned_task.result = (
                step.response
            )

            planned_task.error = (
                step.error
            )

        return workflow

    def preview(
        self,
        task: str,
    ) -> TaskPlan:
        """
        Crea il piano senza eseguire nessun agente.
        Non consuma richieste API.
        """

        return (
            self.create_plan(
                task
            )
        )

    def _build_instruction_with_context(
        self,
        planned_task: PlannedTask,
        previous_results: list[
            WorkflowStepResult
        ],
    ) -> str:

        if not previous_results:

            return (
                planned_task
                .instruction
            )

        context_parts: list[str] = []

        for result in previous_results[-2:]:

            if not result.success:
                continue

            response = (
                result.response
                .strip()
            )

            if not response:
                continue

            context_parts.append(
                (
                    f"RISULTATO DI "
                    f"{result.agent_name}:\n"
                    f"{response}"
                )
            )

        if not context_parts:

            return (
                planned_task
                .instruction
            )

        context = (
            "\n\n".join(
                context_parts
            )
        )

        if (
            len(context)
            > self._max_context_characters
        ):

            context = (
                context[
                    -self._max_context_characters:
                ]
            )

        return (
            f"{planned_task.instruction}\n\n"
            "CONTESTO DALLE FASI PRECEDENTI:\n"
            f"{context}\n\n"
            "Usa il contesto solo se utile. "
            "Non ripetere inutilmente il lavoro "
            "degli agenti precedenti."
        )

    @staticmethod
    def _requires_api(
        agent: Agent,
    ) -> bool:

        provider = (
            agent.preferred_provider
            or "ollama"
        )

        return (
            provider
            .strip()
            .lower()
            != "ollama"
        )

    @staticmethod
    def _create_local_fallback_agent(
        agent: Agent,
    ) -> Agent:

        return replace(
            agent,
            preferred_provider="ollama",
            preferred_model="qwen3:4b-instruct",
            use_local_model=True,
            max_tokens=min(
                agent.max_tokens,
                128,
            ),
        )

    @staticmethod
    def _convert_result(
        planned_task: PlannedTask,
        agent: Agent,
        execution: AgentExecutionResult,
        used_local_fallback: bool,
    ) -> WorkflowStepResult:

        return WorkflowStepResult(
            task_id=planned_task.task_id,
            agent_id=agent.agent_id,
            agent_name=agent.name,
            success=execution.success,
            provider_name=(
                execution.provider_name
            ),
            response=(
                execution.response
            ),
            used_local_fallback=(
                used_local_fallback
                or execution.used_fallback
            ),
            error=execution.error,
        )