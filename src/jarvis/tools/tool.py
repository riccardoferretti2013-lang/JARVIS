from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolResult:
    """Risultato restituito dall'esecuzione di un tool."""

    success: bool
    message: str
    data: Any | None = None


class Tool(ABC):
    """Interfaccia comune per tutti i tool di J.A.R.V.I.S."""

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        raise NotImplementedError

    @property
    def requires_confirmation(self) -> bool:
        return False

    @property
    def parameters(self) -> dict[str, Any]:
        return {}

    @abstractmethod
    def execute(self, **arguments: Any) -> ToolResult:
        raise NotImplementedError

    def get_definition(self) -> dict[str, Any]:
        """
        Restituisce la definizione del tool nel formato
        compatibile con il tool calling di Ollama.
        """

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": [],
                },
            },
        }