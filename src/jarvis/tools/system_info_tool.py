import platform

from .tool import Tool, ToolResult


class SystemInfoTool(Tool):
    """
    Restituisce informazioni di base sul sistema operativo.
    """

    @property
    def name(self) -> str:
        return "system_info"

    @property
    def description(self) -> str:
        return (
            "Restituisce informazioni sul sistema operativo, "
            "sul computer e sulla versione di Python."
        )

    def execute(self, **arguments) -> ToolResult:
        try:
            system_data = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
            }

            message = (
                f"Sistema operativo: {system_data['system']} "
                f"{system_data['release']}. "
                f"Architettura: {system_data['machine']}. "
                f"Python: {system_data['python_version']}."
            )

            return ToolResult(
                success=True,
                message=message,
                data=system_data,
            )

        except Exception as error:
            return ToolResult(
                success=False,
                message=f"Impossibile leggere le informazioni di sistema: {error}",
            )