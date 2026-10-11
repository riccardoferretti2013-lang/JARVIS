import os
import subprocess
from pathlib import Path

from .application_launcher import ApplicationLauncher


class ExcelController:
    """
    Gestisce Microsoft Excel su Windows.
    """

    def __init__(
        self,
        launcher: ApplicationLauncher | None = None,
    ) -> None:
        self._launcher = (
            launcher
            or ApplicationLauncher()
        )

    def find_excel(
        self,
    ) -> Path | None:
        """
        Cerca Microsoft Excel nelle installazioni
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
            / "EXCEL.EXE",

            program_files_x86
            / "Microsoft Office"
            / "root"
            / "Office16"
            / "EXCEL.EXE",

            program_files
            / "Microsoft Office"
            / "Office16"
            / "EXCEL.EXE",

            program_files_x86
            / "Microsoft Office"
            / "Office16"
            / "EXCEL.EXE",
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
        return self.find_excel() is not None

    def open(
        self,
    ) -> bool:
        """
        Avvia Microsoft Excel.
        """

        excel_path = self.find_excel()

        if excel_path is None:
            return False

        try:
            subprocess.Popen(
                [str(excel_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            return True

        except OSError:
            return False

    def open_workbook(
        self,
        workbook_path: str | Path,
    ) -> bool:
        """
        Apre un file Excel specifico.
        """

        excel_path = self.find_excel()

        if excel_path is None:
            return False

        workbook = Path(
            workbook_path
        )

        if not workbook.exists():
            return False

        try:
            subprocess.Popen(
                [
                    str(excel_path),
                    str(workbook),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            return True

        except OSError:
            return False