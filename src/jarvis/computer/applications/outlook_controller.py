import os
import subprocess
from pathlib import Path

from .application_launcher import ApplicationLauncher


class OutlookController:
    """
    Gestisce Microsoft Outlook su Windows.
    """

    def __init__(
        self,
        launcher: ApplicationLauncher | None = None,
    ) -> None:
        self._launcher = (
            launcher
            or ApplicationLauncher()
        )

    def find_outlook(
        self,
    ) -> Path | None:
        """
        Cerca Outlook nelle installazioni
        desktop classiche di Microsoft Office.
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
            / "OUTLOOK.EXE",

            program_files_x86
            / "Microsoft Office"
            / "root"
            / "Office16"
            / "OUTLOOK.EXE",

            program_files
            / "Microsoft Office"
            / "Office16"
            / "OUTLOOK.EXE",

            program_files_x86
            / "Microsoft Office"
            / "Office16"
            / "OUTLOOK.EXE",
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
        Restituisce True se Outlook
        desktop classico è installato.
        """

        return self.find_outlook() is not None

    def open(
        self,
    ) -> bool:
        """
        Avvia Outlook.
        """

        outlook_path = self.find_outlook()

        if outlook_path is None:
            return False

        try:
            subprocess.Popen(
                [str(outlook_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            return True

        except OSError:
            return False