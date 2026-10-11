import tkinter as tk


class ClipboardController:
    """
    Gestisce gli appunti di Windows.
    """

    def get_text(
        self,
    ) -> str:
        """
        Restituisce il testo presente negli appunti.
        """

        root = self._create_root()

        try:
            text = root.clipboard_get()

            return str(text).strip()

        except tk.TclError:
            return ""

        finally:
            root.destroy()

    def set_text(
        self,
        text: str,
    ) -> bool:
        """
        Scrive un testo negli appunti.
        """

        clean_text = text.strip()

        if not clean_text:
            return False

        root = self._create_root()

        try:
            root.clipboard_clear()
            root.clipboard_append(
                clean_text
            )

            root.update()

            return True

        finally:
            root.destroy()

    def clear(
        self,
    ) -> bool:
        """
        Svuota gli appunti.
        """

        root = self._create_root()

        try:
            root.clipboard_clear()
            root.update()

            return True

        finally:
            root.destroy()

    @staticmethod
    def _create_root() -> tk.Tk:
        root = tk.Tk()

        root.withdraw()

        return root