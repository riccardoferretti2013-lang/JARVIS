from __future__ import annotations

from dataclasses import dataclass

from src.jarvis.agents.agent import Agent
from src.jarvis.agents.agent_registry import AgentRegistry


@dataclass(slots=True)
class AgentSelection:
    """
    Risultato della selezione di un agente.
    """

    agent: Agent | None
    score: int
    reason: str


class AgentSelector:
    """
    Selettore semplice degli agenti.

    In questa prima versione usa parole chiave.
    In futuro potrà usare:
    - embeddings;
    - classificazione AI;
    - Ollama;
    - modelli API;
    - storico dei task;
    - priorità e carico degli agenti.
    """

    def __init__(self, registry: AgentRegistry) -> None:
        self._registry = registry

        self._keyword_map: dict[str, set[str]] = {
            "project_manager": {
                "progetto",
                "pianifica",
                "pianificare",
                "organizza",
                "organizzare",
                "priorità",
                "roadmap",
                "task",
                "attività",
                "scadenza",
                "coordinare",
                "coordina",
            },

            "backend_architect": {
                "backend",
                "api",
                "database",
                "sql",
                "python",
                "server",
                "servizio",
                "architettura",
                "endpoint",
                "flask",
                "fastapi",
                "repository",
                "provider",
            },

            "frontend_developer": {
                "frontend",
                "qml",
                "pyside",
                "pyside6",
                "gui",
                "interfaccia",
                "layout",
                "pagina",
                "finestra",
                "grafica",
                "sidebar",
                "dashboard",
            },

            "research_agent": {
                "ricerca",
                "ricercare",
                "cerca",
                "confronta",
                "confrontare",
                "analizza",
                "analisi",
                "documentazione",
                "fonti",
                "studio",
                "informazioni",
            },

            "qa_engineer": {
                "test",
                "bug",
                "errore",
                "debug",
                "verifica",
                "controlla",
                "controllare",
                "qualità",
                "regressione",
                "sicurezza",
                "problema",
            },
        }

    def select(self, task: str) -> AgentSelection:
        """
        Seleziona l'agente più adatto per il task.
        """

        normalized_task = self._normalize(task)

        if not normalized_task:
            return AgentSelection(
                agent=None,
                score=0,
                reason="Task vuoto.",
            )

        best_agent: Agent | None = None
        best_score = 0
        matched_keywords: list[str] = []

        for agent_id, keywords in self._keyword_map.items():
            agent = self._registry.get(agent_id)

            if agent is None:
                continue

            if not agent.enabled:
                continue

            current_matches = [
                keyword
                for keyword in keywords
                if keyword in normalized_task
            ]

            score = len(current_matches)

            if score > best_score:
                best_score = score
                best_agent = agent
                matched_keywords = current_matches

        if best_agent is None:
            return AgentSelection(
                agent=None,
                score=0,
                reason="Nessun agente specializzato trovato.",
            )

        return AgentSelection(
            agent=best_agent,
            score=best_score,
            reason=(
                "Parole chiave rilevate: "
                + ", ".join(sorted(matched_keywords))
            ),
        )

    def select_or_default(
        self,
        task: str,
        default_agent_id: str = "project_manager",
    ) -> AgentSelection:
        """
        Se non trova un agente specifico, usa un agente di fallback.
        """

        selection = self.select(task)

        if selection.agent is not None:
            return selection

        default_agent = self._registry.get(default_agent_id)

        if default_agent is None:
            return selection

        if not default_agent.enabled:
            return selection

        return AgentSelection(
            agent=default_agent,
            score=0,
            reason=(
                "Nessuna specializzazione rilevata. "
                f"Usato agente di fallback: {default_agent.name}."
            ),
        )

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(
            value.strip().lower().split()
        )