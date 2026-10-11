from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolCall:
    """
    Richiesta di esecuzione di un tool generata dal modello AI.
    """

    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AIResponse:
    """
    Risposta normalizzata restituita da un provider AI.

    Può contenere:
    - una risposta testuale;
    - una o più richieste di tool;
    - entrambe le cose.
    """

    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)

    @property
    def has_tool_calls(self) -> bool:
        """Indica se il modello ha richiesto almeno un tool."""

        return bool(self.tool_calls)

    @property
    def has_content(self) -> bool:
        """Indica se il modello ha restituito del testo."""

        return bool(self.content.strip())