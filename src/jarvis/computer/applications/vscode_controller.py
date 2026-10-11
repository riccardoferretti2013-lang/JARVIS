import os
import subprocess
from pathlib import Path

from .application_launcher import ApplicationLauncher


class VSCodeController:
    """
    Gestisce Visual Studio Code su Windows.
    """

    def __init__(
        self,
        launcher: ApplicationLauncher | None = None,
    ) -> None:
        self._launcher = (
            launcher
            or ApplicationLauncher()
        )

    def find_vscode(
        self,
    ) -> Path | None:
        possible_paths = [
            Path(
                os.environ.get(
                    "LOCALAPPDATA",
                    "",
                )
            )
            / "Programs"
            / "Microsoft VS Code"
            / "Code.exe",

            Path(
                os.environ.get(
                    "PROGRAMFILES",
                    "",
                )
            )
            / "Microsoft VS Code"
            / "Code.exe",

            Path(
                os.environ.get(
                    "PROGRAMFILES(X86)",
                    "",
                )
            )
            / "Microsoft VS Code"
            / "Code.exe",
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
        return self.find_vscode() is not None

    def open(
        self,
        new_window: bool = True,
    ) -> bool:
        vscode_path = self.find_vscode()

        if vscode_path is None:
            return False

        arguments = [
            str(vscode_path)
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

    def open_path(
        self,
        path: str | Path,
        new_window: bool = True,
    ) -> bool:
        vscode_path = self.find_vscode()

        if vscode_path is None:
            return False

        target_path = Path(
            path
        )

        arguments = [
            str(vscode_path)
        ]

        if new_window:
            arguments.append(
                "--new-window"
            )

        arguments.append(
            str(target_path)
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