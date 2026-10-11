import ctypes


class LockController:
    """
    Gestisce il blocco della sessione Windows.
    """

    @staticmethod
    def lock() -> bool:
        """
        Blocca immediatamente la sessione Windows.

        Restituisce True se il comando
        viene accettato correttamente.
        """

        try:
            result = ctypes.windll.user32.LockWorkStation()

            return bool(result)

        except Exception:
            return False