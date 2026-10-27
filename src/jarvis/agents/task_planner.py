from __future__ import annotations

from dataclasses import dataclass, field

from src.jarvis.agents.agent_registry import AgentRegistry


@dataclass(slots=True)
class PlannedTask:
    """
    Singolo task assegnato a un agente.
    """

    task_id: int

    agent_id: str

    instruction: str

    completed: bool = False

    result: str = ""

    error: str | None = None


@dataclass(slots=True)
class TaskPlan:
    """
    Piano di lavoro multi-agent.
    """

    original_task: str

    tasks: list[PlannedTask] = field(
        default_factory=list
    )

    @property
    def task_count(self) -> int:
        return len(self.tasks)

    @property
    def completed_count(self) -> int:

        return sum(
            1
            for task in self.tasks
            if task.completed
        )

    def is_empty(self) -> bool:
        return not self.tasks

    def is_completed(self) -> bool:

        if not self.tasks:
            return False

        return all(
            task.completed
            for task in self.tasks
        )


class TaskPlanner:
    """
    Planner iniziale della AI Company.

    Decide quali agenti devono partecipare
    a un incarico complesso.

    Questa versione usa regole locali e non
    consuma token/API.
    """

    def __init__(
        self,
        registry: AgentRegistry,
    ) -> None:

        self._registry = registry

    def create_plan(
        self,
        task: str,
    ) -> TaskPlan:

        clean_task = (
            task
            .strip()
        )

        plan = TaskPlan(
            original_task=clean_task
        )

        if not clean_task:
            return plan

        normalized = (
            self._normalize(
                clean_task
            )
        )

        selected_agents: list[str] = []

        # -----------------------------------------
        # PROJECT MANAGER
        # -----------------------------------------

        if self._contains_any(
            normalized,
            {
                "progetto",
                "progetta",
                "pianifica",
                "piano",
                "roadmap",
                "applicazione",
                "software",
                "sistema",
                "sviluppa",
                "crea",
            },
        ):

            selected_agents.append(
                "project_manager"
            )

        # -----------------------------------------
        # BACKEND
        # -----------------------------------------

        if self._contains_any(
            normalized,
            {
                "backend",
                "python",
                "api",
                "database",
                "sql",
                "server",
                "endpoint",
                "servizio",
                "provider",
                "architettura",
            },
        ):

            selected_agents.append(
                "backend_architect"
            )

        # -----------------------------------------
        # FRONTEND
        # -----------------------------------------

        if self._contains_any(
            normalized,
            {
                "frontend",
                "qml",
                "pyside",
                "pyside6",
                "gui",
                "interfaccia",
                "pagina",
                "dashboard",
                "layout",
                "grafica",
                "finestra",
                "web",
            },
        ):

            selected_agents.append(
                "frontend_developer"
            )

        # -----------------------------------------
        # RESEARCH
        # -----------------------------------------

        if self._contains_any(
            normalized,
            {
                "ricerca",
                "ricercare",
                "cerca",
                "confronta",
                "confrontare",
                "studia",
                "analizza",
                "documentazione",
                "fonti",
                "informazioni",
                "valuta",
            },
        ):

            selected_agents.append(
                "research_agent"
            )

        # -----------------------------------------
        # QA
        # -----------------------------------------

        if self._contains_any(
            normalized,
            {
                "test",
                "verifica",
                "controlla",
                "bug",
                "errore",
                "debug",
                "sicurezza",
                "qualità",
                "regressione",
            },
        ):

            selected_agents.append(
                "qa_engineer"
            )

        # -----------------------------------------
        # FALLBACK
        # -----------------------------------------

        if not selected_agents:

            selected_agents.append(
                "project_manager"
            )

        selected_agents = (
            self._remove_duplicates(
                selected_agents
            )
        )

        # -----------------------------------------
        # QA FINALE AUTOMATICO
        # -----------------------------------------

        technical_agents = {
            "backend_architect",
            "frontend_developer",
        }

        contains_technical_work = any(
            agent_id in technical_agents
            for agent_id in selected_agents
        )

        if (
            contains_technical_work
            and "qa_engineer"
            not in selected_agents
        ):

            selected_agents.append(
                "qa_engineer"
            )

        # -----------------------------------------
        # CREAZIONE DEL PIANO
        # -----------------------------------------

        task_id = 1

        for agent_id in selected_agents:

            agent = (
                self._registry
                .get(agent_id)
            )

            if agent is None:
                continue

            if not agent.enabled:
                continue

            plan.tasks.append(
                PlannedTask(
                    task_id=task_id,
                    agent_id=agent_id,
                    instruction=(
                        self._build_instruction(
                            agent_id=agent_id,
                            original_task=clean_task,
                        )
                    ),
                )
            )

            task_id += 1

        return plan

    @staticmethod
    def _build_instruction(
        agent_id: str,
        original_task: str,
    ) -> str:

        instructions = {
            "project_manager": (
                "Analizza l'incarico e definisci "
                "obiettivi, priorità, dipendenze "
                "e strategia di esecuzione."
            ),

            "backend_architect": (
                "Occupati degli aspetti backend: "
                "architettura, Python, API, servizi "
                "e database."
            ),

            "frontend_developer": (
                "Occupati degli aspetti frontend: "
                "GUI, QML, layout ed esperienza utente."
            ),

            "research_agent": (
                "Ricerca e analizza le informazioni "
                "necessarie per supportare il lavoro."
            ),

            "qa_engineer": (
                "Verifica il lavoro prodotto cercando "
                "bug, incoerenze, regressioni, rischi "
                "e possibili miglioramenti."
            ),
        }

        specialization = (
            instructions.get(
                agent_id,
                (
                    "Analizza l'incarico secondo "
                    "la tua specializzazione."
                ),
            )
        )

        return (
            "INCARICO GENERALE:\n"
            f"{original_task}\n\n"
            "TUO COMPITO:\n"
            f"{specialization}"
        )

    @staticmethod
    def _contains_any(
        text: str,
        keywords: set[str],
    ) -> bool:

        return any(
            keyword in text
            for keyword in keywords
        )

    @staticmethod
    def _remove_duplicates(
        values: list[str],
    ) -> list[str]:

        result: list[str] = []

        for value in values:

            if value not in result:
                result.append(value)

        return result

    @staticmethod
    def _normalize(
        value: str,
    ) -> str:

        return " ".join(
            value
            .strip()
            .lower()
            .split()
        )