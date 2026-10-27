from __future__ import annotations

from collections.abc import Iterable

from src.jarvis.agents.agent import Agent


class AgentRegistry:
    """
    Registro centrale degli agenti disponibili nella AI Company.

    J.A.R.V.I.S. utilizzerà questo registro per:
    - conoscere gli agenti disponibili;
    - cercare un agente specifico;
    - filtrare gli agenti per dipartimento;
    - abilitare/disabilitare agenti;
    - scegliere in futuro gli agenti necessari per un task.
    """

    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        agent_id = self._normalize_id(agent.agent_id)

        if agent_id in self._agents:
            raise ValueError(
                f"Esiste già un agente con ID '{agent.agent_id}'."
            )

        self._agents[agent_id] = agent

    def register_many(self, agents: Iterable[Agent]) -> None:
        for agent in agents:
            self.register(agent)

    def unregister(self, agent_id: str) -> Agent | None:
        normalized_id = self._normalize_id(agent_id)
        return self._agents.pop(normalized_id, None)

    def get(self, agent_id: str) -> Agent | None:
        normalized_id = self._normalize_id(agent_id)
        return self._agents.get(normalized_id)

    def require(self, agent_id: str) -> Agent:
        agent = self.get(agent_id)

        if agent is None:
            raise KeyError(
                f"Agente '{agent_id}' non trovato nel registry."
            )

        return agent

    def exists(self, agent_id: str) -> bool:
        normalized_id = self._normalize_id(agent_id)
        return normalized_id in self._agents

    def all(self) -> list[Agent]:
        return list(self._agents.values())

    def enabled(self) -> list[Agent]:
        return [
            agent
            for agent in self._agents.values()
            if agent.enabled
        ]

    def disabled(self) -> list[Agent]:
        return [
            agent
            for agent in self._agents.values()
            if not agent.enabled
        ]

    def by_department(
        self,
        department: str,
        *,
        enabled_only: bool = True,
    ) -> list[Agent]:

        normalized_department = self._normalize_text(department)

        agents = []

        for agent in self._agents.values():

            if self._normalize_text(agent.department) != normalized_department:
                continue

            if enabled_only and not agent.enabled:
                continue

            agents.append(agent)

        return agents

    def search(
        self,
        query: str,
        *,
        enabled_only: bool = True,
    ) -> list[Agent]:

        normalized_query = self._normalize_text(query)

        if not normalized_query:
            return self.enabled() if enabled_only else self.all()

        results = []

        for agent in self._agents.values():

            if enabled_only and not agent.enabled:
                continue

            searchable_text = " ".join(
                [
                    agent.agent_id,
                    agent.name,
                    agent.role,
                    agent.department,
                    agent.description,
                ]
            )

            if normalized_query in self._normalize_text(searchable_text):
                results.append(agent)

        return results

    def enable(self, agent_id: str) -> None:
        agent = self.require(agent_id)
        agent.enable()

    def disable(self, agent_id: str) -> None:
        agent = self.require(agent_id)
        agent.disable()

    def count(self) -> int:
        return len(self._agents)

    def count_enabled(self) -> int:
        return len(self.enabled())

    def clear(self) -> None:
        self._agents.clear()

    @staticmethod
    def _normalize_id(value: str) -> str:
        return value.strip().lower()

    @staticmethod
    def _normalize_text(value: str) -> str:
        return " ".join(
            value.strip().lower().split()
        )