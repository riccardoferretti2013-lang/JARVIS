import os
import subprocess
from pathlib import Path

from .application_launcher import ApplicationLauncher


class WordController:
    """
    Gestisce Microsoft Word su Windows.
    """

    def __init__(
        self,
        launcher: ApplicationLauncher | None = None,
    ) -> None:
        self._launcher = (
            launcher
            or ApplicationLauncher()
        )

    def find_word(
        self,
    ) -> Path | None:
        """
        Cerca Microsoft Word nelle installazioni
        comuni di Microsoft Office.
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
            / "WINWORD.EXE",

            program_files_x86
            / "Microsoft Office"
            / "root"
            / "Office16"
            / "WINWORD.EXE",

            program_files
            / "Microsoft Office"
            / "Office16"
            / "WINWORD.EXE",

            program_files_x86
            / "Microsoft Office"
            / "Office16"
            / "WINWORD.EXE",
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
        return self.find_word() is not None

    def open(
        self,
    ) -> bool:
        word_path = self.find_word()

        if word_path is None:
            return False

        try:
            subprocess.Popen(
                [str(word_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            return True

        except OSError:
            return False

    def open_document(
        self,
        document_path: str | Path,
    ) -> bool:
        word_path = self.find_word()

        if word_path is None:
            return False

        document = Path(
            document_path
        )

        if not document.exists():
            return False

        try:
            subprocess.Popen(
                [
                    str(word_path),
                    str(document),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            return True

        except OSError:
            return False