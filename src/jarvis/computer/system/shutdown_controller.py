import subprocess
import sys


class ShutdownController:
    """
    Gestisce lo spegnimento di Windows.
    """

    @staticmethod
    def is_supported() -> bool:
        return sys.platform == "win32"

    def shutdown(
        self,
        delay_seconds: int = 10,
    ) -> bool:
        """
        Pianifica lo spegnimento di Windows.
        """

        if not self.is_supported():
            return False

        delay = max(
            0,
            int(delay_seconds),
        )

        try:
            result = subprocess.run(
                [
                    "shutdown",
                    "/s",
                    "/t",
                    str(delay),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            return result.returncode == 0

        except OSError:
            return False

    def cancel(
        self,
    ) -> bool:
        """
        Annulla uno spegnimento programmato.
        """

        if not self.is_supported():
            return False

        try:
            result = subprocess.run(
                [
                    "shutdown",
                    "/a",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            return result.returncode == 0

        except OSError:
            return False