import os
import subprocess
from pathlib import Path

from .application_launcher import ApplicationLauncher


class TeamsController:
    """
    Gestisce Microsoft Teams su Windows.
    """

    def __init__(
        self,
        launcher: ApplicationLauncher | None = None,
    ) -> None:
        self._launcher = (
            launcher
            or ApplicationLauncher()
        )

    def find_teams(
        self,
    ) -> Path | None:
        """
        Cerca Microsoft Teams
        nelle installazioni più comuni.
        """

        local_app_data = Path(
            os.environ.get(
                "LOCALAPPDATA",
                "",
            )
        )

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
            local_app_data
            / "Microsoft"
            / "Teams"
            / "current"
            / "Teams.exe",

            local_app_data
            / "Microsoft"
            / "WindowsApps"
            / "ms-teams.exe",

            program_files
            / "Microsoft"
            / "Teams"
            / "current"
            / "Teams.exe",

            program_files_x86
            / "Microsoft"
            / "Teams"
            / "current"
            / "Teams.exe",
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
        Restituisce True se Teams è installato.
        """

        return self.find_teams() is not None

    def open(
        self,
    ) -> bool:
        """
        Avvia Microsoft Teams.
        """

        teams_path = self.find_teams()

        if teams_path is None:
            return False

        try:
            subprocess.Popen(
                [str(teams_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            return True

        except OSError:
            return False