import os
import subprocess
from pathlib import Path

from .application_launcher import ApplicationLauncher


class FirefoxController:
    """
    Gestisce Mozilla Firefox su Windows.
    """

    def __init__(
        self,
        launcher: ApplicationLauncher | None = None,
    ) -> None:
        self._launcher = (
            launcher
            or ApplicationLauncher()
        )

    def find_firefox(
        self,
    ) -> Path | None:
        possible_paths = [
            Path(
                os.environ.get(
                    "PROGRAMFILES",
                    "",
                )
            )
            / "Mozilla Firefox"
            / "firefox.exe",

            Path(
                os.environ.get(
                    "PROGRAMFILES(X86)",
                    "",
                )
            )
            / "Mozilla Firefox"
            / "firefox.exe",

            Path(
                os.environ.get(
                    "LOCALAPPDATA",
                    "",
                )
            )
            / "Mozilla Firefox"
            / "firefox.exe",
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
        return self.find_firefox() is not None

    def open(
        self,
        new_window: bool = True,
    ) -> bool:
        firefox_path = self.find_firefox()

        if firefox_path is None:
            return False

        arguments = [
            str(firefox_path)
        ]

        if new_window:
            arguments.append(
                "-new-window"
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
        firefox_path = self.find_firefox()

        if firefox_path is None:
            return False

        clean_url = url.strip()

        if not clean_url:
            return False

        try:
            subprocess.Popen(
                [
                    str(firefox_path),
                    clean_url,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            return True

        except OSError:
            return False