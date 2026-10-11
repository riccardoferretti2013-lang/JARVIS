import os
from pathlib import Path

try:
    import winreg
except ImportError:
    winreg = None


class SpotifyController:
    """
    Controller per Spotify su Windows.
    """

    def is_installed(
        self,
    ) -> bool:

        # Spotify installato in AppData
        appdata = os.environ.get(
            "APPDATA",
            "",
        )

        if appdata:

            spotify_exe = (
                Path(appdata)
                / "Spotify"
                / "Spotify.exe"
            )

            if spotify_exe.exists():
                return True

        # Controllo protocollo spotify:
        if winreg is not None:

            try:

                with winreg.OpenKey(
                    winreg.HKEY_CLASSES_ROOT,
                    "spotify",
                ):
                    return True

            except OSError:
                pass

        # Potrebbe comunque essere installato
        # tramite Microsoft Store.
        return True

    def open(
        self,
    ) -> bool:

        try:

            os.startfile(
                "spotify:"
            )

            return True

        except OSError:
            pass

        # Fallback installazione classica
        appdata = os.environ.get(
            "APPDATA",
            "",
        )

        if appdata:

            spotify_exe = (
                Path(appdata)
                / "Spotify"
                / "Spotify.exe"
            )

            if spotify_exe.exists():

                try:

                    os.startfile(
                        str(
                            spotify_exe
                        )
                    )

                    return True

                except OSError:
                    pass

        return False