from typing import Any

from .system_info_tool import SystemInfoTool
from .tool import Tool, ToolResult


class ToolManager:
    """
    Registra, ricerca ed esegue i tool disponibili.

    I tool predefiniti vengono registrati automaticamente
    durante l'inizializzazione.
    """

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """
        Registra i tool inclusi di default in J.A.R.V.I.S.
        """

        self.register(SystemInfoTool())

    def register(self, tool: Tool) -> None:
        """
        Registra un nuovo tool.
        """

        if not isinstance(tool, Tool):
            raise TypeError(
                "Il tool deve implementare l'interfaccia Tool."
            )

        tool_name = tool.name.strip().lower()

        if not tool_name:
            raise ValueError(
                "Il nome del tool non può essere vuoto."
            )

        if tool_name in self._tools:
            raise ValueError(
                f"Il tool '{tool_name}' è già registrato."
            )

        self._tools[tool_name] = tool

    def unregister(self, tool_name: str) -> None:
        """
        Rimuove un tool dal registro.
        """

        normalized_name = tool_name.strip().lower()
        self._tools.pop(normalized_name, None)

    def get(self, tool_name: str) -> Tool | None:
        """
        Restituisce un tool tramite il suo nome.
        """

        normalized_name = tool_name.strip().lower()
        return self._tools.get(normalized_name)

    def has_tool(self, tool_name: str) -> bool:
        """
        Verifica se un tool è registrato.
        """

        return self.get(tool_name) is not None

    def list_tools(self) -> list[dict[str, Any]]:
        """
        Restituisce le definizioni di tutti i tool registrati.
        """

        return [
            tool.get_definition()
            for tool in self._tools.values()
        ]

    def execute(
        self,
        tool_name: str,
        **arguments: Any,
    ) -> ToolResult:
        """
        Esegue un tool registrato.
        """

        tool = self.get(tool_name)

        if tool is None:
            return ToolResult(
                success=False,
                message=(
                    f"Il tool '{tool_name}' non è disponibile."
                ),
            )

        if tool.requires_confirmation:
            return ToolResult(
                success=False,
                message=(
                    f"Il tool '{tool.name}' richiede conferma "
                    "prima dell'esecuzione."
                ),
                data={
                    "requires_confirmation": True,
                    "tool_name": tool.name,
                    "arguments": arguments,
                },
            )

        try:
            return tool.execute(**arguments)

        except Exception as error:
            return ToolResult(
                success=False,
                message=(
                    f"Errore durante l'esecuzione del tool "
                    f"'{tool.name}': {error}"
                ),
            )