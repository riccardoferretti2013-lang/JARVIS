from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .tool import ToolResult
from .tool_manager import ToolManager

if TYPE_CHECKING:
    from ..ai.ai_response import ToolCall


class ToolExecutor:
    """
    Esegue in modo controllato i tool richiesti dall'AI.

    Non dipende da Ollama o da altri provider:
    riceve una richiesta normalizzata tramite ToolCall.
    """

    def __init__(
        self,
        tool_manager: ToolManager | None = None,
    ) -> None:
        self._tool_manager = tool_manager or ToolManager()

    @property
    def tool_manager(self) -> ToolManager:
        return self._tool_manager

    def execute(
        self,
        tool_name: str,
        **arguments: Any,
    ) -> ToolResult:
        """
        Esegue un tool usando nome e argomenti.
        """

        return self._tool_manager.execute(
            tool_name,
            **arguments,
        )

    def execute_call(self, tool_call: ToolCall) -> ToolResult:
        """
        Esegue una richiesta di tool generata dal modello AI.
        """

        clean_name = tool_call.name.strip().lower()

        if not clean_name:
            return ToolResult(
                success=False,
                message="La richiesta AI non contiene il nome del tool.",
            )

        if not self.has_tool(clean_name):
            return ToolResult(
                success=False,
                message=f"Il tool '{clean_name}' non è disponibile.",
            )

        return self.execute(
            clean_name,
            **tool_call.arguments,
        )

    def available_tools(self) -> list[dict[str, Any]]:
        """
        Restituisce le definizioni dei tool disponibili.
        """

        return self._tool_manager.list_tools()

    def has_tool(self, tool_name: str) -> bool:
        """
        Controlla se un tool è registrato.
        """

        return self._tool_manager.has_tool(tool_name)