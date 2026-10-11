from .conversation_summary import ConversationSummary
from .summary_repository import SummaryRepository

from ..provider import Message
from ..provider_manager import ProviderManager


class SummaryService:
    """
    Genera e salva riassunti automatici
    della conversazione.
    """

    def __init__(
        self,
        provider_manager: ProviderManager | None = None,
        repository: SummaryRepository | None = None,
    ) -> None:
        self._provider_manager = (
            provider_manager
            or ProviderManager()
        )

        self._repository = (
            repository
            or SummaryRepository()
        )

    @property
    def provider_manager(
        self,
    ) -> ProviderManager:
        return self._provider_manager

    @property
    def repository(
        self,
    ) -> SummaryRepository:
        return self._repository

    def summarize(
        self,
        messages: list[Message],
    ) -> ConversationSummary | None:
        conversation_text = (
            self._build_conversation_text(
                messages
            )
        )

        if not conversation_text:
            return None

        previous_summary = (
            self._repository.get()
        )

        prompt_messages = (
            self._build_summary_messages(
                conversation_text=conversation_text,
                previous_summary=previous_summary,
            )
        )

        response = (
            self._provider_manager
            .provider
            .generate(
                prompt_messages
            )
            .strip()
        )

        if not response:
            return None

        if response.startswith(
            (
                "Errore Ollama:",
                "Errore imprevisto di Ollama:",
            )
        ):
            return None

        summary = ConversationSummary(
            content=response,
            summarized_messages=len(messages),
        )

        return self._repository.save(
            summary
        )

    def get_summary(
        self,
    ) -> ConversationSummary | None:
        return self._repository.get()

    def get_summary_content(
        self,
    ) -> str:
        summary = self.get_summary()

        if summary is None:
            return ""

        return summary.content

    def clear(self) -> None:
        self._repository.clear()

    def _build_summary_messages(
        self,
        conversation_text: str,
        previous_summary: ConversationSummary | None,
    ) -> list[Message]:
        previous_content = (
            previous_summary.content
            if previous_summary is not None
            else "Nessun riassunto precedente."
        )

        system_content = """
Sei il componente interno che riassume le conversazioni di J.A.R.V.I.S.

Il tuo unico compito è creare un riassunto della conversazione fornita.

REGOLE OBBLIGATORIE:
- Non rispondere alle domande presenti nella conversazione.
- Non continuare la conversazione.
- Non parlare direttamente con l'utente.
- Non spiegare gli argomenti citati.
- Riassumi ciò che utente e assistente hanno detto.
- Scrivi sempre in italiano.
- Conserva decisioni, obiettivi, preferenze e informazioni importanti.
- Conserva nomi di persone, progetti, tecnologie, file e percorsi.
- Conserva problemi riscontrati e soluzioni applicate.
- Non inventare informazioni.
- Ignora saluti e frasi senza valore per il contesto.
- Restituisci soltanto il riassunto.
- Non scrivere titoli o introduzioni come "Ecco il riassunto".
- Usa una forma breve, chiara e impersonale.
""".strip()

        user_content = f"""
Devi aggiornare il riassunto della conversazione.

<RIASSUNTO_PRECEDENTE>
{previous_content}
</RIASSUNTO_PRECEDENTE>

<CONVERSAZIONE_DA_RIASSUMERE>
{conversation_text}
</CONVERSAZIONE_DA_RIASSUMERE>

Genera un unico riassunto aggiornato.
Non rispondere alle domande contenute nella conversazione.
""".strip()

        return [
            {
                "role": "system",
                "content": system_content,
            },
            {
                "role": "user",
                "content": user_content,
            },
        ]

    @staticmethod
    def _build_conversation_text(
        messages: list[Message],
    ) -> str:
        lines: list[str] = []

        for message in messages:
            role = str(
                message.get(
                    "role",
                    "unknown",
                )
            ).strip()

            content = str(
                message.get(
                    "content",
                    "",
                )
                or ""
            ).strip()

            if not content:
                continue

            if role == "system":
                continue

            role_name = {
                "user": "Utente",
                "assistant": "J.A.R.V.I.S.",
                "tool": "Risultato tool",
            }.get(
                role,
                role.title(),
            )

            lines.append(
                f"{role_name}: {content}"
            )

        return "\n".join(lines)