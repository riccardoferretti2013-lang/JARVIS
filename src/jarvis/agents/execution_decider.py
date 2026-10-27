from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ExecutionDecision:
    mode: str
    reason: str
    estimated_complexity: int

    @property
    def use_workflow(self) -> bool:
        return self.mode == "workflow"


class ExecutionDecider:
    """
    Decide se un task deve essere eseguito da:

    - un singolo agente
    - un workflow multi-agent

    Questa versione usa regole locali e non consuma API.
    """

    SIMPLE_KEYWORDS = {
        "spiega",
        "dimmi",
        "cos'è",
        "cosa è",
        "definisci",
        "correggi",
        "controlla",
        "verifica",
        "traduci",
        "riassumi",
    }

    COMPLEX_KEYWORDS = {
        "progetta",
        "sviluppa",
        "crea",
        "costruisci",
        "architettura",
        "applicazione",
        "software",
        "sistema",
        "backend",
        "frontend",
        "database",
        "api",
        "sicurezza",
        "integra",
        "implementa",
        "roadmap",
        "workflow",
    }

    def decide(
        self,
        task: str,
    ) -> ExecutionDecision:

        clean_task = self._normalize(
            task
        )

        if not clean_task:

            return ExecutionDecision(
                mode="single",
                reason="Task vuoto.",
                estimated_complexity=0,
            )

        score = 0

        simple_hits = self._count_hits(
            clean_task,
            self.SIMPLE_KEYWORDS,
        )

        complex_hits = self._count_hits(
            clean_task,
            self.COMPLEX_KEYWORDS,
        )

        score += complex_hits * 2
        score -= simple_hits

        # Task molto lungo = probabilmente più complesso
        if len(clean_task) > 150:
            score += 1

        if len(clean_task) > 300:
            score += 1

        # Più richieste nello stesso messaggio
        separators = (
            " e ",
            " poi ",
            " inoltre ",
            " anche ",
        )

        multi_part = sum(
            1
            for separator in separators
            if separator in clean_task
        )

        score += min(
            multi_part,
            2,
        )

        if score >= 3:

            return ExecutionDecision(
                mode="workflow",
                reason=(
                    "Il task richiede più competenze "
                    "o contiene più fasi."
                ),
                estimated_complexity=score,
            )

        return ExecutionDecision(
            mode="single",
            reason=(
                "Il task può essere gestito "
                "da un singolo agente."
            ),
            estimated_complexity=max(
                score,
                1,
            ),
        )

    @staticmethod
    def _count_hits(
        text: str,
        keywords: set[str],
    ) -> int:

        return sum(
            1
            for keyword in keywords
            if keyword in text
        )

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