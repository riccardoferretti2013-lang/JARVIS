from ...summarization import SummaryManager

from .context_source import ContextSource


class SummaryContextSource(ContextSource):
    """
    Fornisce il riassunto automatico
    della conversazione.
    """

    def __init__(
        self,
        summary_manager: SummaryManager,
    ) -> None:
        self._summary_manager = summary_manager

    @property
    def source_name(self) -> str:
        return "Summary"

    def get_data(self) -> str:
        return (
            self._summary_manager
            .get_summary_content()
        )