import re

from ..agent import AIAgent
from ..applications import PreferredApplicationCommands
from ..automation import AutomationManager
from ..computer import ApplicationCommands
from ..computer.files import FileSearchCommands
from ..computer.system import (
    BrightnessCommands,
    ClipboardCommands,
    LockCommands,
    RestartCommands,
    ScreenshotCommands,
    ShutdownCommands,
    VolumeCommands,
)
from ..contacts import ContactCommands
from ..history import CommandHistory
from ..internet import (
    InternetCommands,
    InternetService,
)
from ..projects import ProjectCommands
from ..remote import RemoteServer
from ..services.service_manager import ServiceManager
from .conversation import Conversation


class Assistant:

    _LAST_COMMANDS = {
        "ultimo comando",
        "qual è stato l'ultimo comando",
        "qual e stato l'ultimo comando",
        "ripeti ultimo comando",
        "ripeti l'ultimo comando",
    }

    _PENULTIMATE_COMMANDS = {
        "penultimo comando",
        "qual è stato il penultimo comando",
        "qual e stato il penultimo comando",
        "ripeti penultimo comando",
        "ripeti il penultimo comando",
    }

    _HISTORY_COMMANDS = {
        "ultimi comandi",
        "utimi comandi",
        "mostra ultimi comandi",
        "mostra utimi comandi",
        "mostra gli ultimi comandi",
        "cronologia comandi",
        "cronologia dei comandi",
        "mostra cronologia comandi",
    }

    _CLEAR_HISTORY_COMMANDS = {
        "cancella cronologia comandi",
        "svuota cronologia comandi",
        "elimina cronologia comandi",
    }

    _COUNT_PATTERN = re.compile(
        (
            r"^(?:mostra\s+)?"
            r"(?:gli\s+)?"
            r"(?:ultimi|utimi)\s+"
            r"(\d+)\s+comandi$"
        ),
        flags=re.IGNORECASE,
    )

    _NUMBER_WORD_PATTERN = re.compile(
        (
            r"^(?:mostra\s+)?"
            r"(?:gli\s+)?"
            r"(?:ultimi|utimi)\s+"
            r"(uno|due|tre|quattro|cinque|sei|sette|otto|nove|dieci)"
            r"\s+comandi$"
        ),
        flags=re.IGNORECASE,
    )

    _NUMBER_WORDS = {
        "uno": 1,
        "due": 2,
        "tre": 3,
        "quattro": 4,
        "cinque": 5,
        "sei": 6,
        "sette": 7,
        "otto": 8,
        "nove": 9,
        "dieci": 10,
    }

    def __init__(
        self,
    ) -> None:

        self.status = "offline"

        # ==========================================
        # CORE
        # ==========================================

        self.services = (
            ServiceManager()
        )

        self.conversation = (
            Conversation(
                self.services
            )
        )

        self.agent = (
            AIAgent()
        )

        # ==========================================
        # CRONOLOGIA
        # ==========================================

        self.command_history = (
            CommandHistory(
                max_size=100
            )
        )

        # ==========================================
        # PROGETTI / CONTATTI
        # ==========================================

        self.project_commands = (
            ProjectCommands()
        )

        self.contact_commands = (
            ContactCommands()
        )

        # ==========================================
        # APPLICAZIONI
        # ==========================================

        self.preferred_application_commands = (
            PreferredApplicationCommands()
        )

        self.application_commands = (
            ApplicationCommands()
        )

        # ==========================================
        # AUTOMATION
        # ==========================================

        self.automation_manager = (
            AutomationManager(
                application_commands=(
                    self.application_commands
                )
            )
        )

        # ==========================================
        # INTERNET
        # ==========================================

        self.internet_service = (
            InternetService()
        )

        self.internet_commands = (
            InternetCommands()
        )

        # ==========================================
        # COMPUTER CONTROL
        # ==========================================

        self.volume_commands = (
            VolumeCommands()
        )

        self.brightness_commands = (
            BrightnessCommands()
        )

        self.screenshot_commands = (
            ScreenshotCommands()
        )

        self.clipboard_commands = (
            ClipboardCommands()
        )

        self.lock_commands = (
            LockCommands()
        )

        self.restart_commands = (
            RestartCommands()
        )

        self.shutdown_commands = (
            ShutdownCommands()
        )

        self.file_search_commands = (
            FileSearchCommands()
        )

        # ==========================================
        # REMOTE API
        # ==========================================
        #
        # Raspberry / telefono
        #       ↓
        # porta 8766
        #       ↓
        # questa stessa istanza di Assistant
        #
        # NON viene creato un secondo J.A.R.V.I.S.
        # ==========================================

        self.remote_server = (
            RemoteServer(
                command_callback=(
                    self.process_command
                ),
                status_callback=(
                    self.get_status
                ),
                host="0.0.0.0",
                port=8766,
            )
        )

    def start(
        self,
    ) -> None:

        self.services.initialize()

        language = (
            self.services.settings.get(
                "language"
            )
        )

        model = (
            self.services.settings.get(
                "whisper_model"
            )
        )

        self.services.logger.info(
            f"Lingua configurata: {language}"
        )

        self.services.logger.info(
            "Modello Whisper configurato: "
            f"{model}"
        )

        self.status = "online"

        # ==========================================
        # REMOTE SERVER
        # ==========================================

        try:

            self.remote_server.start()

            self.services.logger.info(
                "J.A.R.V.I.S. Remote API "
                "avviata sulla porta 8766."
            )

        except Exception as exc:

            self.services.logger.error(
                "Errore avvio Remote API: "
                f"{exc}"
            )

        # ==========================================
        # START COMPLETATO
        # ==========================================

        self.services.logger.info(
            "Sistema J.A.R.V.I.S. avviato."
        )

        self.conversation.reply(
            "Sistema avviato."
        )

        self.conversation.reply(
            "Tutti i sistemi principali "
            "sono operativi."
        )

    def shutdown(
        self,
    ) -> None:

        if self.status == "offline":
            return

        self.services.logger.info(
            "Spegnimento di J.A.R.V.I.S."
        )

        self.conversation.reply(
            "Spegnimento completato."
        )

        self.status = "offline"

        self.services.shutdown()

    def get_status(
        self,
    ) -> str:

        return self.status

    def process_command(
        self,
        command: str,
    ) -> None:

        clean_command = (
            command
            .strip()
            .lower()
        )

        if not clean_command:
            return

        self.services.logger.info(
            f"Comando: {clean_command}"
        )

        # ==========================================
        # CRONOLOGIA
        # ==========================================

        if self._process_history_command(
            clean_command
        ):
            return

        self.command_history.add(
            clean_command
        )

        # ==========================================
        # AUTOMATION
        # ==========================================

        automation_response = (
            self.automation_manager.process(
                clean_command
            )
        )

        if automation_response is not None:

            self.services.logger.info(
                "Automation: "
                f"{automation_response}"
            )

            self.conversation.reply(
                automation_response
            )

            return

        # ==========================================
        # INTERNET
        # ==========================================

        internet_query = (
            self.internet_commands
            .extract_query(
                clean_command
            )
        )

        if internet_query is not None:

            self._process_internet_search(
                internet_query
            )

            return

        # ==========================================
        # APPLICATIONS
        # ==========================================

        application_response = (
            self.application_commands.process(
                clean_command
            )
        )

        if application_response is not None:

            self.conversation.reply(
                application_response
            )

            return

        # ==========================================
        # VOLUME
        # ==========================================

        volume_response = (
            self.volume_commands.process(
                clean_command
            )
        )

        if volume_response is not None:

            self.conversation.reply(
                volume_response
            )

            return

        # ==========================================
        # LUMINOSITA
        # ==========================================

        brightness_response = (
            self.brightness_commands.process(
                clean_command
            )
        )

        if brightness_response is not None:

            self.conversation.reply(
                brightness_response
            )

            return

        # ==========================================
        # SCREENSHOT
        # ==========================================

        screenshot_response = (
            self.screenshot_commands.process(
                clean_command
            )
        )

        if screenshot_response is not None:

            self.conversation.reply(
                screenshot_response
            )

            return

        # ==========================================
        # CLIPBOARD
        # ==========================================

        clipboard_response = (
            self.clipboard_commands.process(
                clean_command
            )
        )

        if clipboard_response is not None:

            self.conversation.reply(
                clipboard_response
            )

            return

        # ==========================================
        # LOCK
        # ==========================================

        lock_response = (
            self.lock_commands.process(
                clean_command
            )
        )

        if lock_response is not None:

            self.conversation.reply(
                lock_response
            )

            return

        # ==========================================
        # RESTART
        # ==========================================

        restart_response = (
            self.restart_commands.process(
                clean_command
            )
        )

        if restart_response is not None:

            self.conversation.reply(
                restart_response
            )

            return

        # ==========================================
        # SHUTDOWN
        # ==========================================

        shutdown_response = (
            self.shutdown_commands.process(
                clean_command
            )
        )

        if shutdown_response is not None:

            self.conversation.reply(
                shutdown_response
            )

            return

        # ==========================================
        # FILE SEARCH
        # ==========================================

        file_search_response = (
            self.file_search_commands.process(
                clean_command
            )
        )

        if file_search_response is not None:

            self.conversation.reply(
                file_search_response
            )

            return

        # ==========================================
        # PROJECTS
        # ==========================================

        project_response = (
            self.project_commands.process(
                clean_command
            )
        )

        if project_response is not None:

            self.conversation.reply(
                project_response
            )

            return

        # ==========================================
        # CONTACTS
        # ==========================================

        contact_response = (
            self.contact_commands.process(
                clean_command
            )
        )

        if contact_response is not None:

            self.conversation.reply(
                contact_response
            )

            return

        # ==========================================
        # PREFERRED APPLICATIONS
        # ==========================================

        preferred_application_response = (
            self.preferred_application_commands
            .process(
                clean_command
            )
        )

        if (
            preferred_application_response
            is not None
        ):

            self.conversation.reply(
                preferred_application_response
            )

            return

        # ==========================================
        # ROUTER
        # ==========================================

        router_response = (
            self.services.router.process(
                clean_command
            )
        )

        if router_response is not None:

            self.conversation.reply(
                router_response
            )

            return

        # ==========================================
        # AI
        # ==========================================

        stream = (
            self.agent.process_stream(
                clean_command
            )
        )

        ai_response = (
            self.conversation.reply_stream(
                stream
            )
        )

        self.services.logger.info(
            f"AI: {ai_response}"
        )

    # ==============================================
    # INTERNET SEARCH
    # ==============================================

    def _process_internet_search(
        self,
        query: str,
    ) -> None:

        self.services.logger.info(
            f"Ricerca internet: {query}"
        )

        results = (
            self.internet_service.search(
                query,
                max_results=5,
            )
        )

        if not results:

            self.conversation.reply(
                "Non sono riuscito a trovare "
                "risultati su Internet."
            )

            return

        web_context = (
            self.internet_service
            .format_results_for_ai(
                results
            )
        )

        prompt = (
            "Rispondi alla richiesta usando "
            "i risultati Internet riportati sotto.\n"
            "Sii sintetico e chiaro.\n"
            "Non inventare informazioni che "
            "non compaiono nei risultati.\n\n"
            f"RICHIESTA:\n{query}\n\n"
            f"RISULTATI WEB:\n{web_context}"
        )

        stream = (
            self.agent.process_stream(
                prompt
            )
        )

        ai_response = (
            self.conversation.reply_stream(
                stream
            )
        )

        self.services.logger.info(
            "Internet/AI: "
            f"{ai_response}"
        )

    # ==============================================
    # HISTORY
    # ==============================================

    def _process_history_command(
        self,
        command: str,
    ) -> bool:

        if command in self._LAST_COMMANDS:

            self._reply_command_at_position(
                position=1,
                label=(
                    "L'ultimo comando è stato"
                ),
            )

            return True

        if (
            command
            in self._PENULTIMATE_COMMANDS
        ):

            self._reply_command_at_position(
                position=2,
                label=(
                    "Il penultimo comando è stato"
                ),
            )

            return True

        if command in self._HISTORY_COMMANDS:

            self._reply_with_command_history(
                count=10
            )

            return True

        if (
            command
            in self._CLEAR_HISTORY_COMMANDS
        ):

            self.command_history.clear()

            self.conversation.reply(
                "La cronologia dei comandi "
                "è stata cancellata."
            )

            return True

        count_match = (
            self._COUNT_PATTERN.fullmatch(
                command
            )
        )

        if count_match is not None:

            self._reply_with_command_history(
                count=int(
                    count_match.group(1)
                )
            )

            return True

        word_match = (
            self._NUMBER_WORD_PATTERN.fullmatch(
                command
            )
        )

        if word_match is not None:

            number_word = (
                word_match
                .group(1)
                .lower()
            )

            self._reply_with_command_history(
                count=(
                    self._NUMBER_WORDS[
                        number_word
                    ]
                )
            )

            return True

        return False

    def _reply_command_at_position(
        self,
        position: int,
        label: str,
    ) -> None:

        saved_command = (
            self.command_history.get(
                position_from_end=position
            )
        )

        if saved_command is None:

            self.conversation.reply(
                "Non ci sono abbastanza "
                "comandi nella cronologia."
            )

            return

        self.conversation.reply(
            f"{label}: {saved_command}"
        )

    def _reply_with_command_history(
        self,
        count: int,
    ) -> None:

        if count < 1:

            self.conversation.reply(
                "Il numero di comandi deve "
                "essere almeno uno."
            )

            return

        count = min(
            count,
            100,
        )

        commands = (
            self.command_history.last(
                count=count
            )
        )

        if not commands:

            self.conversation.reply(
                "Non ci sono ancora comandi "
                "nella cronologia."
            )

            return

        first_number = (
            self.command_history.count()
            - len(commands)
            + 1
        )

        formatted_commands = "\n".join(
            (
                f"{index}. "
                f"{saved_command}"
            )
            for index, saved_command
            in enumerate(
                commands,
                start=first_number,
            )
        )

        self.conversation.reply(
            "Gli ultimi comandi sono:\n"
            f"{formatted_commands}"
        )