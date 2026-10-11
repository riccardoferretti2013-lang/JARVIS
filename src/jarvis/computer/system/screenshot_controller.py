from datetime import datetime
from pathlib import Path

from PIL import ImageGrab


class ScreenshotController:
    """
    Gestisce gli screenshot dello schermo.
    """

    def __init__(
        self,
        output_directory: str | Path | None = None,
    ) -> None:
        if output_directory is None:
            project_root = (
                Path(__file__)
                .resolve()
                .parents[4]
            )

            output_directory = (
                project_root
                / "data"
                / "screenshots"
            )

        self._output_directory = Path(
            output_directory
        )

        self._output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    @property
    def output_directory(
        self,
    ) -> Path:
        return self._output_directory

    def capture(
        self,
    ) -> Path:
        """
        Cattura lo schermo e salva
        lo screenshot su disco.
        """

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        file_path = (
            self._output_directory
            / f"screenshot_{timestamp}.png"
        )

        screenshot = ImageGrab.grab(
            all_screens=True
        )

        screenshot.save(
            file_path,
            format="PNG",
        )

        return file_path

    def capture_to(
        self,
        file_path: str | Path,
    ) -> Path:
        """
        Cattura lo schermo e salva
        lo screenshot in un percorso specifico.
        """

        target = Path(
            file_path
        )

        if target.suffix.lower() != ".png":
            target = target.with_suffix(
                ".png"
            )

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        screenshot = ImageGrab.grab(
            all_screens=True
        )

        screenshot.save(
            target,
            format="PNG",
        )

        return target