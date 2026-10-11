import re
import subprocess
import time

import keyboard
import psutil

from ...computer import ApplicationCommands
from ..routine import Routine


class WorkRoutine(Routine):
    """
    Automazione Modalità Lavoro.

    Sequenza:

    1. Apre Spotify
    2. Apre la playlist Lavoro
    3. Aspetta che Spotify sia pronto
    4. Riporta il brano corrente a 00:00
    5. Avvia la musica
    6. Apre Visual Studio Code
    7. Apre Edge sulla chat J.A.R.V.I.S.
    """

    SPOTIFY_PLAYLIST_ID = (
        "3scU2yehq0yBqsUDOKvLuw"
    )

    SPOTIFY_PLAYLIST_URI = (
        "spotify:playlist:"
        + SPOTIFY_PLAYLIST_ID
    )

    CHATGPT_URL = (
        "https://chatgpt.com/"
        "g/g-p-6a5cef353280819195412eb98de30ba4/"
        "c/6a7036bc-b6f4-83eb-bd41-696077a41e35"
    )

    COMMANDS = {
        "modalità lavoro",
        "modalita lavoro",
        "attiva modalità lavoro",
        "attiva modalita lavoro",
        "avvia modalità lavoro",
        "avvia modalita lavoro",
        "inizia modalità lavoro",
        "inizia modalita lavoro",
        "prepara modalità lavoro",
        "prepara modalita lavoro",
        "modalità lavorativa",
        "modalita lavorativa",
    }

    ACTIVATION_WORDS = {
        "modalità",
        "modalita",
        "qualità",
        "qualita",
        "modo",
        "routine",
        "attiva",
        "avvia",
        "inizia",
        "prepara",
        "lavorativa",
    }

    def __init__(
        self,
        application_commands: (
            ApplicationCommands
            | None
        ) = None,
    ) -> None:

        self._applications = (
            application_commands
            or ApplicationCommands()
        )

    @property
    def name(self) -> str:
        return "Modalità lavoro"

    def matches(
        self,
        command: str,
    ) -> bool:

        clean_command = (
            command
            .strip()
            .lower()
        )

        clean_command = re.sub(
            r"[^\wàèéìòù\s]",
            " ",
            clean_command,
        )

        clean_command = re.sub(
            r"\s+",
            " ",
            clean_command,
        ).strip()

        if clean_command in self.COMMANDS:
            return True

        if "lavoro" not in clean_command:
            return False

        words = set(
            clean_command.split()
        )

        if words & self.ACTIVATION_WORDS:
            return True

        if (
            len(clean_command.split()) <= 4
            and "lavoro" in clean_command
        ):
            return True

        return False

    def execute(
        self,
    ) -> str:

        errors: list[str] = []

        # ==========================================
        # 1. SPOTIFY
        # ==========================================

        try:
            self._open_spotify_playlist()

        except Exception:
            errors.append(
                "Spotify"
            )

        # ==========================================
        # 2. ASPETTA CHE SPOTIFY SIA AVVIATO
        # ==========================================

        spotify_ready = (
            self._wait_for_spotify(
                timeout=15.0
            )
        )

        if not spotify_ready:

            errors.append(
                "avvio Spotify"
            )

        else:

            # Aspettiamo che Spotify e la playlist
            # siano realmente caricati.
            time.sleep(
                3.5
            )

            try:

                # ==================================
                # 3. PORTA PRIMA IL BRANO A 00:00
                # ==================================

                self._restart_current_track()

                # ==================================
                # 4. SOLO ORA AVVIA LA MUSICA
                # ==================================

                self._start_spotify_playback()

            except Exception:

                errors.append(
                    "riproduzione Spotify"
                )

            # La musica deve essere già partita
            # prima di aprire il resto.
            time.sleep(
                2.0
            )

        # ==========================================
        # 5. VISUAL STUDIO CODE
        # ==========================================

        try:

            response = (
                self._applications.process(
                    "apri vs code"
                )
            )

            if (
                response is None
                or "non" in response.lower()
            ):

                errors.append(
                    "Visual Studio Code"
                )

        except Exception:

            errors.append(
                "Visual Studio Code"
            )

        time.sleep(
            1.0
        )

        # ==========================================
        # 6. EDGE + CHAT J.A.R.V.I.S.
        # ==========================================

        try:

            self._open_chat_in_edge()

        except Exception:

            errors.append(
                "ChatGPT"
            )

        # ==========================================
        # RISULTATO
        # ==========================================

        if not errors:

            return (
                "Modalità lavoro attivata."
            )

        failed_items = ", ".join(
            errors
        )

        return (
            "Modalità lavoro avviata, "
            "ma ci sono stati problemi con: "
            f"{failed_items}."
        )

    @staticmethod
    def _open_spotify_playlist(
    ) -> None:

        subprocess.Popen(
            [
                "cmd",
                "/c",
                "start",
                "",
                WorkRoutine.SPOTIFY_PLAYLIST_URI,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=(
                subprocess.CREATE_NO_WINDOW
                if hasattr(
                    subprocess,
                    "CREATE_NO_WINDOW",
                )
                else 0
            ),
        )

    @staticmethod
    def _wait_for_spotify(
        timeout: float,
    ) -> bool:

        start_time = (
            time.monotonic()
        )

        while (
            time.monotonic()
            - start_time
            < timeout
        ):

            for process in (
                psutil.process_iter(
                    ["name"]
                )
            ):

                try:

                    process_name = (
                        process.info.get(
                            "name"
                        )
                        or ""
                    ).lower()

                    if (
                        process_name
                        == "spotify.exe"
                    ):

                        return True

                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                ):
                    continue

            time.sleep(
                0.3
            )

        return False

    @staticmethod
    def _restart_current_track(
    ) -> None:
        """
        Riporta il brano corrente all'inizio
        PRIMA di avviare la riproduzione.
        """

        keyboard.press_and_release(
            "previous track"
        )

        time.sleep(
            0.8
        )

    @staticmethod
    def _start_spotify_playback(
    ) -> None:
        """
        Avvia la riproduzione solo dopo
        che il brano è stato riportato a 00:00.
        """

        keyboard.press_and_release(
            "play/pause media"
        )

        time.sleep(
            0.5
        )

    @staticmethod
    def _open_chat_in_edge(
    ) -> None:

        subprocess.Popen(
            [
                "cmd",
                "/c",
                "start",
                "",
                "msedge",
                WorkRoutine.CHATGPT_URL,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=(
                subprocess.CREATE_NO_WINDOW
                if hasattr(
                    subprocess,
                    "CREATE_NO_WINDOW",
                )
                else 0
            ),
        )