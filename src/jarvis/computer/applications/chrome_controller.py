import os
from pathlib import Path

from .application_launcher import ApplicationLauncher


class ChromeController:
    """
    Gestisce Google Chrome su Windows.
    """

    def __init__(
        self,
        launcher: ApplicationLauncher | None = None,
    ) -> None:
        self._launcher = (
            launcher
            or ApplicationLauncher()
        )

    def find_chrome(
        self,
    ) -> Path | None:
        possible_paths = [
            Path(
                os.environ.get(
                    "PROGRAMFILES",
                    "",
                )
            )
            / "Google"
            / "Chrome"
            / "Application"
            / "chrome.exe",

            Path(
                os.environ.get(
                    "PROGRAMFILES(X86)",
                    "",
                )
            )
            / "Google"
            / "Chrome"
            / "Application"
            / "chrome.exe",

            Path(
                os.environ.get(
                    "LOCALAPPDATA",
                    "",
                )
            )
            / "Google"
            / "Chrome"
            / "Application"
            / "chrome.exe",
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
        return self.find_chrome() is not None

    def open(
        self,
    ) -> bool:
        chrome_path = self.find_chrome()

        if chrome_path is None:
            return False

        return self._launcher.open_executable(
            chrome_path
        )