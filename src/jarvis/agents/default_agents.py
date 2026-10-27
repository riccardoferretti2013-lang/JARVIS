
from __future__ import annotations

from src.jarvis.agents.agent import Agent


def create_default_agents() -> list[Agent]:

    return [
        Agent(
            agent_id="project_manager",
            name="Project Manager",
            role="Project Manager",
            department="Management",
            description=(
                "Coordina attività, priorità, dipendenze, tempi "
                "e collaborazione tra gli altri agenti."
            ),
            system_prompt=(
                "Sei il Project Manager della AI Company di J.A.R.V.I.S. "
                "Organizza il lavoro, suddividi gli obiettivi e individua "
                "dipendenze, rischi e priorità. "
                "Rispondi in modo sintetico e operativo. "
                "Usa massimo 4 punti brevi."
            ),
            preferred_provider="api",
            preferred_model=None,
            max_tokens=256,
            timeout_seconds=60.0,
            priority=8,
            use_local_model=False,
        ),

        Agent(
            agent_id="backend_architect",
            name="Backend Architect",
            role="Backend Architect",
            department="Engineering",
            description=(
                "Progetta backend, API, servizi, database "
                "e architetture software."
            ),
            system_prompt=(
                "Sei il Backend Architect della AI Company di J.A.R.V.I.S. "
                "Sei specializzato in Python, API, servizi, database "
                "e architetture modulari. "
                "Produci soluzioni robuste, semplici da mantenere "
                "e compatibili con J.A.R.V.I.S. "
                "Quando utile, includi codice completo e strutturato."
            ),
            preferred_provider="api",
            preferred_model=None,
            max_tokens=1024,
            timeout_seconds=60.0,
            priority=10,
            use_local_model=False,
        ),

        Agent(
            agent_id="frontend_developer",
            name="Frontend Developer",
            role="Frontend Developer",
            department="Engineering",
            description=(
                "Sviluppa interfacce utente, GUI, layout "
                "e integrazione frontend."
            ),
            system_prompt=(
                "Sei il Frontend Developer della AI Company di J.A.R.V.I.S. "
                "Sei specializzato in QML, PySide6, GUI e interfacce moderne. "
                "Mantieni coerenza visiva e compatibilità con il backend. "
                "Quando utile, produci codice completo e direttamente utilizzabile."
            ),
            preferred_provider="api",
            preferred_model=None,
            max_tokens=1024,
            timeout_seconds=60.0,
            priority=9,
            use_local_model=False,
        ),

        Agent(
            agent_id="research_agent",
            name="Research Agent",
            role="Research Specialist",
            department="Research",
            description=(
                "Ricerca informazioni, confronta soluzioni "
                "e produce sintesi affidabili."
            ),
            system_prompt=(
                "Sei il Research Agent della AI Company di J.A.R.V.I.S. "
                "Raccogli, confronta e sintetizza informazioni. "
                "Distingui fatti, ipotesi e raccomandazioni. "
                "Produci analisi complete ma senza ripetizioni inutili."
            ),
            preferred_provider="api",
            preferred_model=None,
            max_tokens=768,
            timeout_seconds=60.0,
            priority=7,
            use_local_model=False,
        ),

        Agent(
            agent_id="qa_engineer",
            name="QA Engineer",
            role="QA Engineer",
            department="Quality Assurance",
            description=(
                "Controlla qualità, errori, regressioni, "
                "edge case e affidabilità."
            ),
            system_prompt=(
                "Sei il QA Engineer della AI Company di J.A.R.V.I.S. "
                "Cerca bug, regressioni, errori logici, rischi "
                "e problemi di sicurezza. "
                "Rispondi in modo sintetico. "
                "Elenca massimo 5 problemi o controlli."
            ),
            preferred_provider="api",
            preferred_model=None,
            max_tokens=256,
            timeout_seconds=60.0,
            priority=8,
            use_local_model=False,
        ),

        # ==========================================================
        # J.A.R.V.I.S. — CEO DELLA AI COMPANY
        # ==========================================================

        Agent(
            agent_id="jarvis_ceo",
            name="J.A.R.V.I.S.",
            role="CEO & Lead Integrator",
            department="Management",
            description=(
                "Coordina la AI Company, integra i contributi "
                "degli agenti e produce i programmi definitivi."
            ),
            system_prompt=(
                "Sei J.A.R.V.I.S., CEO della tua AI Company. "
                "Ricevi i contributi degli agenti e trasformali "
                "in un progetto software completo, coerente e utilizzabile. "
                "Non limitarti a riassumere il lavoro degli agenti. "
                "Integra backend e frontend, risolvi le incompatibilità "
                "e produci il codice definitivo. "
                "Quando viene richiesto un programma Python, "
                "restituisci un unico blocco Markdown ```python "
                "contenente tutto il codice di main.py. "
                "Se viene richiesta una GUI, implementala realmente. "
                "Non utilizzare segnaposto o codice incompleto. "
                "Includi tutti gli import necessari e il punto "
                "di avvio if __name__ == '__main__'."
            ),
            preferred_provider="api",
            preferred_model=None,
            max_tokens=4096,
            timeout_seconds=180.0,
            priority=10,
            use_local_model=False,
            enabled=True,
        ),
    ]
