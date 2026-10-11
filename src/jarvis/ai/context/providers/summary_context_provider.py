from ..context_block import ContextBlock
from ..sources import SummaryContextSource
from .context_provider import ContextProvider


class SummaryContextProvider(ContextProvider):
    """
    Inserisce il riassunto della conversazione
    nel contesto AI.
    """

    def __init__(
        self,
        source: SummaryContextSource,
    ) -> None:
        self._source = source

    @property
    def provider_name(self) -> str:
        return "Summary"

    @property
    def priority(self) -> int:
        return 85

    def get_context(self) -> ContextBlock:
        summary = self._source.get_data().strip()

        if not summary:
            return ContextBlock(
                name=self.provider_name,
                priority=self.priority,
                messages=[],
            )

        return ContextBlock(
            name=self.provider_name,
            priority=self.priority,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "RIASSUNTO DELLA CONVERSAZIONE PRECEDENTE:\n"
                        f"{summary}"
                    ),
                }
            ],
        )