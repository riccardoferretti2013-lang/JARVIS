from .chrome_controller import ChromeController
from .edge_controller import EdgeController
from .excel_controller import ExcelController
from .firefox_controller import FirefoxController
from .outlook_controller import OutlookController
from .powerpoint_controller import PowerPointController
from .spotify_controller import SpotifyController
from .teams_controller import TeamsController
from .vscode_controller import VSCodeController
from .word_controller import WordController


class ApplicationCommands:
    """
    Gestisce i comandi relativi alle applicazioni.
    """

    def __init__(
        self,
        chrome_controller: ChromeController | None = None,
        edge_controller: EdgeController | None = None,
        firefox_controller: FirefoxController | None = None,
        vscode_controller: VSCodeController | None = None,
        outlook_controller: OutlookController | None = None,
        teams_controller: TeamsController | None = None,
        word_controller: WordController | None = None,
        excel_controller: ExcelController | None = None,
        powerpoint_controller: PowerPointController | None = None,
        spotify_controller: SpotifyController | None = None,
    ) -> None:

        self._chrome = (
            chrome_controller
            or ChromeController()
        )

        self._edge = (
            edge_controller
            or EdgeController()
        )

        self._firefox = (
            firefox_controller
            or FirefoxController()
        )

        self._vscode = (
            vscode_controller
            or VSCodeController()
        )

        self._outlook = (
            outlook_controller
            or OutlookController()
        )

        self._teams = (
            teams_controller
            or TeamsController()
        )

        self._word = (
            word_controller
            or WordController()
        )

        self._excel = (
            excel_controller
            or ExcelController()
        )

        self._powerpoint = (
            powerpoint_controller
            or PowerPointController()
        )

        self._spotify = (
            spotify_controller
            or SpotifyController()
        )

    def process(
        self,
        command: str,
    ) -> str | None:

        clean_command = (
            command
            .strip()
            .lower()
        )

        if not clean_command:
            return None

        # ==========================================
        # SPOTIFY
        # ==========================================

        if clean_command in {
            "apri spotify",
            "avvia spotify",
            "apri spotifai",
            "avvia spotifai",
            "apri spotyfy",
            "avvia spotyfy",
        }:

            return self._open_spotify()

        # ==========================================
        # CHROME
        # ==========================================

        if clean_command in {
            "apri chrome",
            "avvia chrome",
            "apri google chrome",
            "avvia google chrome",
        }:

            return self._open_chrome()

        # ==========================================
        # EDGE
        # ==========================================

        if clean_command in {
            "apri edge",
            "avvia edge",
            "apri microsoft edge",
            "avvia microsoft edge",
            "apri il browser",
            "apri browser",
            "avvia il browser",
            "avvia browser",
        }:

            return self._open_edge()

        # ==========================================
        # FIREFOX
        # ==========================================

        if clean_command in {
            "apri firefox",
            "avvia firefox",
            "apri mozilla firefox",
            "avvia mozilla firefox",
        }:

            return self._open_firefox()

        # ==========================================
        # VS CODE
        # ==========================================

        if clean_command in {
            "apri vs code",
            "avvia vs code",
            "apri vscode",
            "avvia vscode",
            "apri visual studio code",
            "avvia visual studio code",
            "apri editor",
            "apri l'editor",
        }:

            return self._open_vscode()

        # ==========================================
        # OUTLOOK
        # ==========================================

        if clean_command in {
            "apri outlook",
            "avvia outlook",
            "apri microsoft outlook",
            "avvia microsoft outlook",
        }:

            return self._open_outlook()

        # ==========================================
        # TEAMS
        # ==========================================

        if clean_command in {
            "apri teams",
            "avvia teams",
            "apri microsoft teams",
            "avvia microsoft teams",
        }:

            return self._open_teams()

        # ==========================================
        # WORD
        # ==========================================

        if clean_command in {
            "apri word",
            "avvia word",
            "apri microsoft word",
            "avvia microsoft word",
        }:

            return self._open_word()

        # ==========================================
        # EXCEL
        # ==========================================

        if clean_command in {
            "apri excel",
            "avvia excel",
            "apri microsoft excel",
            "avvia microsoft excel",
            "apri exel",
            "avvia exel",
        }:

            return self._open_excel()

        # ==========================================
        # POWERPOINT
        # ==========================================

        if clean_command in {
            "apri powerpoint",
            "avvia powerpoint",
            "apri power point",
            "avvia power point",
            "apri microsoft powerpoint",
            "avvia microsoft powerpoint",
        }:

            return self._open_powerpoint()

        return None

    # ==============================================
    # SPOTIFY
    # ==============================================

    def _open_spotify(
        self,
    ) -> str:

        if not self._spotify.is_installed():

            return (
                "Spotify non è installato "
                "su questo computer."
            )

        if not self._spotify.open():

            return (
                "Non sono riuscito ad aprire "
                "Spotify."
            )

        return "Spotify aperto."

    # ==============================================
    # CHROME
    # ==============================================

    def _open_chrome(
        self,
    ) -> str:

        if not self._chrome.is_installed():

            return (
                "Google Chrome non è installato "
                "su questo computer."
            )

        if not self._chrome.open():

            return (
                "Non sono riuscito ad aprire "
                "Google Chrome."
            )

        return "Google Chrome aperto."

    # ==============================================
    # EDGE
    # ==============================================

    def _open_edge(
        self,
    ) -> str:

        if not self._edge.is_installed():

            return (
                "Microsoft Edge non è installato "
                "su questo computer."
            )

        if not self._edge.open(
            new_window=True
        ):

            return (
                "Non sono riuscito ad aprire "
                "Microsoft Edge."
            )

        return "Microsoft Edge aperto."

    # ==============================================
    # FIREFOX
    # ==============================================

    def _open_firefox(
        self,
    ) -> str:

        if not self._firefox.is_installed():

            return (
                "Mozilla Firefox non è installato "
                "su questo computer."
            )

        if not self._firefox.open(
            new_window=True
        ):

            return (
                "Non sono riuscito ad aprire "
                "Mozilla Firefox."
            )

        return "Mozilla Firefox aperto."

    # ==============================================
    # VS CODE
    # ==============================================

    def _open_vscode(
        self,
    ) -> str:

        if not self._vscode.is_installed():

            return (
                "Visual Studio Code non è installato "
                "su questo computer."
            )

        if not self._vscode.open(
            new_window=True
        ):

            return (
                "Non sono riuscito ad aprire "
                "Visual Studio Code."
            )

        return "Visual Studio Code aperto."

    # ==============================================
    # OUTLOOK
    # ==============================================

    def _open_outlook(
        self,
    ) -> str:

        if not self._outlook.is_installed():

            return (
                "Microsoft Outlook non è installato "
                "su questo computer."
            )

        if not self._outlook.open():

            return (
                "Non sono riuscito ad aprire "
                "Microsoft Outlook."
            )

        return "Microsoft Outlook aperto."

    # ==============================================
    # TEAMS
    # ==============================================

    def _open_teams(
        self,
    ) -> str:

        if not self._teams.is_installed():

            return (
                "Microsoft Teams non è installato "
                "su questo computer."
            )

        if not self._teams.open():

            return (
                "Non sono riuscito ad aprire "
                "Microsoft Teams."
            )

        return "Microsoft Teams aperto."

    # ==============================================
    # WORD
    # ==============================================

    def _open_word(
        self,
    ) -> str:

        if not self._word.is_installed():

            return (
                "Microsoft Word non è installato "
                "su questo computer."
            )

        if not self._word.open():

            return (
                "Non sono riuscito ad aprire "
                "Microsoft Word."
            )

        return "Microsoft Word aperto."

    # ==============================================
    # EXCEL
    # ==============================================

    def _open_excel(
        self,
    ) -> str:

        if not self._excel.is_installed():

            return (
                "Microsoft Excel non è installato "
                "su questo computer."
            )

        if not self._excel.open():

            return (
                "Non sono riuscito ad aprire "
                "Microsoft Excel."
            )

        return "Microsoft Excel aperto."

    # ==============================================
    # POWERPOINT
    # ==============================================

    def _open_powerpoint(
        self,
    ) -> str:

        if not self._powerpoint.is_installed():

            return (
                "Microsoft PowerPoint non è installato "
                "su questo computer."
            )

        if not self._powerpoint.open():

            return (
                "Non sono riuscito ad aprire "
                "Microsoft PowerPoint."
            )

        return "Microsoft PowerPoint aperto."