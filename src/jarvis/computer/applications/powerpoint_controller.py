import os
import subprocess
from pathlib import Path

from .application_launcher import ApplicationLauncher


class PowerPointController:
    """
    Gestisce Microsoft PowerPoint su Windows.
    """

    def __init__(
        self,
        launcher: ApplicationLauncher | None = None,
    ) -> None:
        self._launcher = (
            launcher
            or ApplicationLauncher()
        )

    def find_powerpoint(
        self,
    ) -> Path | None:
        """
        Cerca Microsoft PowerPoint nelle
        installazioni comuni di Microsoft Office.
        """

        program_files = Path(
            os.environ.get(
                "PROGRAMFILES",
                "",
            )
        )

        program_files_x86 = Path(
            os.environ.get(
                "PROGRAMFILES(X86)",
                "",
            )
        )

        possible_paths = [
            program_files
            / "Microsoft Office"
            / "root"
            / "Office16"
            / "POWERPNT.EXE",

            program_files_x86
            / "Microsoft Office"
            / "root"
            / "Office16"
            / "POWERPNT.EXE",

            program_files
            / "Microsoft Office"
            / "Office16"
            / "POWERPNT.EXE",

            program_files_x86
            / "Microsoft Office"
            / "Office16"
            / "POWERPNT.EXE",
        ]

        return (
            self._launcher
            .find_first_existing(
                possible_paths
            )
        )

    def is_installed(
        self,
    ) -> bool:
        """
        Restituisce True se PowerPoint
        è installato.
        """

        return self.find_powerpoint() is not None

    def open(
        self,
    ) -> bool:
        """
        Avvia Microsoft PowerPoint.
        """

        powerpoint_path = self.find_powerpoint()

        if powerpoint_path is None:
            return False

        try:
            subprocess.Popen(
                [str(powerpoint_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            return True

        except OSError:
            return False

    def open_presentation(
        self,
        presentation_path: str | Path,
    ) -> bool:
        """
        Apre una presentazione PowerPoint specifica.
        """

        powerpoint_path = self.find_powerpoint()

        if powerpoint_path is None:
            return False

        presentation = Path(
            presentation_path
        )

        if not presentation.exists():
            return False

        try:
            subprocess.Popen(
                [
                    str(powerpoint_path),
                    str(presentation),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            return True

        except OSError:
            return False