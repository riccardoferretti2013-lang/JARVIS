from pathlib import Path

from .screenshot_controller import ScreenshotController


class ScreenshotCommands:
    """
    Gestisce i comandi relativi
    agli screenshot.
    """

    def __init__(
        self,
        controller: ScreenshotController | None = None,
    ) -> None:
        self._controller = (
            controller
            or ScreenshotController()
        )

    def process(
        self,
        command: str,
    ) -> str | None:
        clean_command = (
            command
            .strip()
            .lower()
        )

        if not clean_command:
            return None

        if clean_command in {
            "screenshot",
            "fai screenshot",
            "fai uno screenshot",
            "fai uno screen",
            "cattura schermo",
            "cattura lo schermo",
            "salva screenshot",
            "salva uno screenshot",
        }:
            return self._capture()

        return None

    def _capture(
        self,
    ) -> str:
        try:
            path = (
                self._controller.capture()
            )

        except Exception:
            return (
                "Non sono riuscito a catturare "
                "lo schermo."
            )

        return self._build_success_message(
            path
        )

    @staticmethod
    def _build_success_message(
        path: Path,
    ) -> str:
        return (
            "Screenshot acquisito e salvato in "
            f"{path}."
        )