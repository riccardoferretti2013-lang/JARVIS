from ..context_block import ContextBlock
from ..sources import MemoryContextSource
from .context_provider import ContextProvider


class MemoryContextProvider(ContextProvider):
    """
    Converte i ricordi selezionati
    nel contesto per il modello AI.
    """

    def __init__(
        self,
        source: MemoryContextSource,
    ) -> None:
        self._source = source

    @property
    def provider_name(
        self,
    ) -> str:
        return "Memory"

    @property
    def priority(
        self,
    ) -> int:
        return 100

    def get_context(
        self,
    ) -> ContextBlock:
        memories = self._source.get_data()

        if not memories:
            return ContextBlock(
                name=self.provider_name,
                priority=self.priority,
                messages=[],
            )

        lines = [
            "INFORMAZIONI PERMANENTI SULL'UTENTE:",
            (
                "Le informazioni seguenti appartengono esclusivamente "
                "all'utente Riccardo, non a J.A.R.V.I.S."
            ),
        ]

        for memory in memories:
            lines.append(
                f"- {memory.key}: {memory.value}"
            )

        lines.extend(
            [
                "",
                "REGOLE DI UTILIZZO:",
                "- Parla di queste informazioni usando 'tu', 'tuo' e 'tua'.",
                "- Non attribuire queste informazioni a J.A.R.V.I.S.",
                "- Non dichiarare di avere configurato applicazioni o sistemi.",
            ]
        )

        return ContextBlock(
            name=self.provider_name,
            priority=self.priority,
            messages=[
                {
                    "role": "system",
                    "content": "\n".join(lines),
                }
            ],
        )