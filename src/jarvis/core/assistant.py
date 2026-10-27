from __future__ import annotations

import re

from ..agent import AIAgent
from ..agents import CompanyManager
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
from ..projects import ProjectCommands
from ..services.service_manager import ServiceManager
from .conversation import Conversation


class Assistant:
    """
    Classe principale di J.A.R.V.I.S.

    Pipeline principale:

    1. Cronologia
    2. Automation
    3. Computer Control
    4. Progetti / Contatti
    5. Command Router
    6. AI Company
    7. AI generale J.A.R.V.I.S.
    """

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

    _COMPANY_KEYWORDS = {
        "api",
        "backend",
        "frontend",
        "database",
        "sql",
        "python",
        "codice",
        "programma",
        "programmare",
        "software",
        "applicazione",
        "architettura",
        "qml",
        "pyside",
        "pyside6",
        "gui",
        "interfaccia",
        "server",
        "endpoint",
        "debug",
        "bug",
        "test",
        "sicurezza",
        "ricerca",
        "ricerca web",
        "confronta",
        "analizza",
        "progetta",
        "sviluppa",
        "implementa",
        "costruisci",
        "roadmap",
        "workflow",
    }

    def __init__(self) -> None:

        self.status = "offline"

        self.services = ServiceManager()

        self.conversation = Conversation(
            self.services
        )

        # ==========================================
        # AI GENERALE
        # ==========================================

        self.agent = AIAgent()

        # ==========================================
        # AI COMPANY
        # ==========================================

        self.company = CompanyManager()

        # ==========================================
        # CRONOLOGIA
        # ==========================================

        self.command_history = CommandHistory(
            max_size=100
        )

        # ==========================================
        # PROGETTI
        # ==========================================

        self.project_commands = (
            ProjectCommands()
        )

        # ==========================================
        # CONTATTI
        # ==========================================

        self.contact_commands = (
            ContactCommands()
        )

        # ==========================================
        # APPLICAZIONI PREFERITE
        # ==========================================

        self.preferred_application_commands = (
            PreferredApplicationCommands()
        )

        # ==========================================
        # COMPUTER CONTROL
        # ==========================================

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
        # SYSTEM CONTROL
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

        # ==========================================
        # FILE
        # ==========================================

        self.file_search_commands = (
            FileSearchCommands()
        )

    def start(self) -> None:

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
            f"Modello Whisper configurato: {model}"
        )

        self.status = "online"

        self.services.logger.info(
            "Sistema J.A.R.V.I.S. avviato."
        )

        self.conversation.reply(
            "Sistema avviato."
        )

        self.conversation.reply(
            "Tutti i sistemi principali sono operativi."
        )

    def shutdown(self) -> None:

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

    def get_status(self) -> str:

        return self.status

    def process_command(
        self,
        command: str,
    ) -> None:

        original_command = (
            command.strip()
        )

        clean_command = (
            original_command.lower()
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
        # IMPORTANTE:
        # deve essere PRIMA di AI Company / OpenAI
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
        # APPLICAZIONI
        # ==========================================

        application_response = (
            self.application_commands.process(
                clean_command
            )
        )

        if application_response is not None:

            self.services.logger.info(
                "Computer/Application: "
                f"{application_response}"
            )

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

            self.services.logger.info(
                "Computer/Volume: "
                f"{volume_response}"
            )

            self.conversation.reply(
                volume_response
            )

            return

        # ==========================================
        # LUMINOSITÀ
        # ==========================================

        brightness_response = (
            self.brightness_commands.process(
                clean_command
            )
        )

        if brightness_response is not None:

            self.services.logger.info(
                "Computer/Brightness: "
                f"{brightness_response}"
            )

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

            self.services.logger.info(
                "Computer/Screenshot: "
                f"{screenshot_response}"
            )

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

            self.services.logger.info(
                "Computer/Clipboard: "
                f"{clipboard_response}"
            )

            self.conversation.reply(
                clipboard_response
            )

            return

        # ==========================================
        # BLOCCO PC
        # ==========================================

        lock_response = (
            self.lock_commands.process(
                clean_command
            )
        )

        if lock_response is not None:

            self.services.logger.info(
                "Computer/Lock: "
                f"{lock_response}"
            )

            self.conversation.reply(
                lock_response
            )

            return

        # ==========================================
        # RIAVVIO
        # ==========================================

        restart_response = (
            self.restart_commands.process(
                clean_command
            )
        )

        if restart_response is not None:

            self.services.logger.info(
                "Computer/Restart: "
                f"{restart_response}"
            )

            self.conversation.reply(
                restart_response
            )

            return

        # ==========================================
        # SPEGNIMENTO
        # ==========================================

        shutdown_response = (
            self.shutdown_commands.process(
                clean_command
            )
        )

        if shutdown_response is not None:

            self.services.logger.info(
                "Computer/Shutdown: "
                f"{shutdown_response}"
            )

            self.conversation.reply(
                shutdown_response
            )

            return

        # ==========================================
        # FILE
        # ==========================================

        file_search_response = (
            self.file_search_commands.process(
                clean_command
            )
        )

        if file_search_response is not None:

            self.services.logger.info(
                "Computer/FileSearch: "
                f"{file_search_response}"
            )

            self.conversation.reply(
                file_search_response
            )

            return

        # ==========================================
        # PROGETTI
        # ==========================================

        project_response = (
            self.project_commands.process(
                clean_command
            )
        )

        if project_response is not None:

            self.services.logger.info(
                f"Progetti: {project_response}"
            )

            self.conversation.reply(
                project_response
            )

            return

        # ==========================================
        # CONTATTI
        # ==========================================

        contact_response = (
            self.contact_commands.process(
                clean_command
            )
        )

        if contact_response is not None:

            self.services.logger.info(
                f"Contatti: {contact_response}"
            )

            self.conversation.reply(
                contact_response
            )

            return

        # ==========================================
        # APPLICAZIONI PREFERITE
        # ==========================================

        preferred_application_response = (
            self.preferred_application_commands
            .process(
                clean_command
            )
        )

        if preferred_application_response is not None:

            self.services.logger.info(
                "Applicazioni preferite: "
                f"{preferred_application_response}"
            )

            self.conversation.reply(
                preferred_application_response
            )

            return

        # ==========================================
        # COMMAND ROUTER
        # ==========================================

        router_response = (
            self.services.router.process(
                clean_command
            )
        )

        if router_response is not None:

            self.services.logger.info(
                f"Router: {router_response}"
            )

            self.conversation.reply(
                router_response
            )

            return

        # ==========================================
        # AI COMPANY
        # ==========================================

        if self._should_use_company(
            clean_command
        ):

            company_response = (
                self._process_with_company(
                    original_command
                )
            )

            if company_response is not None:

                self.services.logger.info(
                    "AI Company: "
                    f"{company_response}"
                )

                self.conversation.reply(
                    company_response
                )

                return

        # ==========================================
        # AI GENERALE J.A.R.V.I.S.
        # ==========================================

        stream = (
            self.agent.process_stream(
                original_command
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

    def _should_use_company(
        self,
        command: str,
    ) -> bool:

        decision = (
            self.company
            .preview_execution(
                command
            )
        )

        if decision.use_workflow:
            return True

        return any(
            keyword in command
            for keyword in self._COMPANY_KEYWORDS
        )

    def _process_with_company(
        self,
        command: str,
    ) -> str | None:

        try:

            result = (
                self.company
                .execute_auto(
                    command
                )
            )

        except Exception as error:

            self.services.logger.error(
                "Errore AI Company: "
                f"{error}"
            )

            return None

        # ==========================================
        # SINGOLO AGENTE
        # ==========================================

        if result.mode == "single":

            single = (
                result.single_result
            )

            if single is None:
                return None

            if not single.success:
                return None

            response = (
                single.response.strip()
            )

            if not response:
                return None

            return response

        # ==========================================
        # WORKFLOW MULTI-AGENT
        # ==========================================

        workflow = (
            result.workflow_result
        )

        if workflow is None:
            return None

        successful_steps = [
            step
            for step in workflow.steps
            if (
                step.success
                and step.response.strip()
            )
        ]

        if not successful_steps:
            return None

        preferred_order = [
            "project_manager",
            "backend_architect",
            "frontend_developer",
            "research_agent",
            "qa_engineer",
        ]

        labels = {
            "project_manager": "Piano",
            "backend_architect": "Backend",
            "frontend_developer": "Frontend",
            "research_agent": "Ricerca",
            "qa_engineer": "Verifica finale",
        }

        step_map = {
            step.agent_id: step
            for step in successful_steps
        }

        sections: list[str] = []

        for agent_id in preferred_order:

            step = (
                step_map.get(
                    agent_id
                )
            )

            if step is None:
                continue

            label = (
                labels.get(
                    agent_id,
                    step.agent_name,
                )
            )

            sections.append(
                (
                    f"## {label}\n\n"
                    f"{step.response.strip()}"
                )
            )

        if not sections:
            return None

        header = (
            "Ho completato il lavoro con "
            f"{len(successful_steps)} agenti "
            "specializzati."
        )

        if workflow.failed_steps:

            header += (
                f" {workflow.failed_steps} agente/i "
                "non hanno completato correttamente "
                "il proprio passaggio."
            )

        return (
            f"{header}\n\n"
            + "\n\n".join(
                sections
            )
        )

    def _process_history_command(
        self,
        command: str,
    ) -> bool:

        if command in self._LAST_COMMANDS:

            self._reply_command_at_position(
                position=1,
                label="L'ultimo comando è stato",
            )

            return True

        if command in self._PENULTIMATE_COMMANDS:

            self._reply_command_at_position(
                position=2,
                label="Il penultimo comando è stato",
            )

            return True

        if command in self._HISTORY_COMMANDS:

            self._reply_with_command_history(
                count=10
            )

            return True

        if command in self._CLEAR_HISTORY_COMMANDS:

            self.command_history.clear()

            self.conversation.reply(
                "La cronologia dei comandi è stata cancellata."
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
                word_match.group(1).lower()
            )

            self._reply_with_command_history(
                count=self._NUMBER_WORDS[
                    number_word
                ]
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
                "Non ci sono abbastanza comandi nella cronologia."
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
                "Il numero di comandi deve essere almeno uno."
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
                "Non ci sono ancora comandi nella cronologia."
            )

            return

        first_number = (
            self.command_history.count()
            - len(commands)
            + 1
        )

        formatted_commands = "\n".join(
            f"{index}. {saved_command}"
            for index, saved_command in enumerate(
                commands,
                start=first_number,
            )
        )

        self.conversation.reply(
            "Gli ultimi comandi sono:\n"
            f"{formatted_commands}"
        )