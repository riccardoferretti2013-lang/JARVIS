import os
import subprocess
from pathlib import Path

from .application_launcher import ApplicationLauncher


class EdgeController:
    """
    Gestisce Microsoft Edge su Windows.
    """

    def __init__(
        self,
        launcher: ApplicationLauncher | None = None,
    ) -> None:
        self._launcher = (
            launcher
            or ApplicationLauncher()
        )

    def find_edge(
        self,
    ) -> Path | None:
        """
        Cerca l'eseguibile di Microsoft Edge.
        """

        possible_paths = [
            Path(
                os.environ.get(
                    "PROGRAMFILES(X86)",
                    "",
                )
            )
            / "Microsoft"
            / "Edge"
            / "Application"
            / "msedge.exe",

            Path(
                os.environ.get(
                    "PROGRAMFILES",
                    "",
                )
            )
            / "Microsoft"
            / "Edge"
            / "Application"
            / "msedge.exe",

            Path(
                os.environ.get(
                    "LOCALAPPDATA",
                    "",
                )
            )
            / "Microsoft"
            / "Edge"
            / "Application"
            / "msedge.exe",
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
        return self.find_edge() is not None

    def open(
        self,
        new_window: bool = True,
    ) -> bool:
        """
        Apre Microsoft Edge.

        Se Edge è già aperto, new_window=True
        forza l'apertura di una nuova finestra.
        """

        edge_path = self.find_edge()

        if edge_path is None:
            return False

        arguments = [
            str(edge_path)
        ]

        if new_window:
            arguments.append(
                "--new-window"
            )

        try:
            subprocess.Popen(
                arguments,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            return True

        except OSError:
            return False

    def open_url(
        self,
        url: str,
    ) -> bool:
        """
        Apre un indirizzo web specificamente
        con Microsoft Edge.
        """

        edge_path = self.find_edge()

        if edge_path is None:
            return False

        clean_url = url.strip()

        if not clean_url:
            return False

        try:
            subprocess.Popen(
                [
                    str(edge_path),
                    clean_url,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            return True

        except OSError:
            return False