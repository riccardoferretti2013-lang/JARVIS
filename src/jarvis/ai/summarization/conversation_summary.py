from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ConversationSummary:
    """
    Rappresenta un riassunto della conversazione.
    """

    content: str
    summarized_messages: int
    summary_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        clean_content = self.content.strip()

        if not clean_content:
            raise ValueError(
                "Il contenuto del riassunto non può essere vuoto."
            )

        if self.summarized_messages < 1:
            raise ValueError(
                "Il numero di messaggi riassunti deve essere almeno uno."
            )

        object.__setattr__(
            self,
            "content",
            clean_content,
        )