import subprocess
import sys


class RestartController:
    """
    Gestisce il riavvio di Windows.
    """

    @staticmethod
    def is_supported() -> bool:
        """
        Verifica che J.A.R.V.I.S.
        sia in esecuzione su Windows.
        """

        return sys.platform == "win32"

    def restart(
        self,
        delay_seconds: int = 10,
    ) -> bool:
        """
        Pianifica il riavvio di Windows.

        Il ritardo permette eventualmente
        di annullare il riavvio.
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
                    "/r",
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
        Annulla un riavvio programmato.
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