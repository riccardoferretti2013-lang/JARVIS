import os
import subprocess
from pathlib import Path


class ApplicationLauncher:
    """
    Gestisce l'apertura delle applicazioni
    installate sul computer.
    """

    def open_executable(
        self,
        executable_path: str | Path,
    ) -> bool:
        path = Path(
            executable_path
        )

        if not path.exists():
            return False

        try:
            subprocess.Popen(
                [str(path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            return True

        except OSError:
            return False

    def open_command(
        self,
        command: str,
    ) -> bool:
        clean_command = command.strip()

        if not clean_command:
            return False

        try:
            subprocess.Popen(
                clean_command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True,
            )

            return True

        except OSError:
            return False

    @staticmethod
    def find_first_existing(
        paths: list[str | Path],
    ) -> Path | None:
        for candidate in paths:
            path = Path(
                os.path.expandvars(
                    str(candidate)
                )
            )

            if path.exists():
                return path

        return None