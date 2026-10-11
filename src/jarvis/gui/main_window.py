import threading

from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..audio.interrupt_listener import (
    InterruptListener,
)
from ..core.assistant import Assistant
from .background_wake import (
    BackgroundWakeListener,
)
from .hud_widgets import (
    FuturisticBackground,
    InfoCard,
    JarvisOrb,
)
from .status_manager import (
    JarvisState,
    StatusManager,
)


class MainWindow(QMainWindow):

    conversation_event = Signal(
        str,
        str,
    )

    state_changed = Signal(
        object
    )

    startup_finished = Signal()

    command_finished = Signal()

    microphone_result = Signal(
        str
    )

    startup_error = Signal(
        str
    )

    def __init__(
        self,
        assistant: Assistant,
    ) -> None:
        super().__init__()

        self._assistant = assistant

        self._busy = False
        self._allow_close = False

        self._interrupt_listener = None
        self._background_wake = None

        self.setWindowTitle(
            "J.A.R.V.I.S. — Advanced Intelligence Interface"
        )

        self.resize(
            1440,
            860,
        )

        self.setMinimumSize(
            1180,
            720,
        )

        self._build_ui()
        self._apply_style()
        self._connect_signals()

        self._assistant.conversation.set_output_callback(
            self._conversation_callback
        )

        self._set_state(
            JarvisState.STARTING
        )

        self._start_assistant()

    def _build_ui(
        self,
    ) -> None:

        root = FuturisticBackground()

        root.setObjectName(
            "root"
        )

        root_layout = QVBoxLayout(
            root
        )

        root_layout.setContentsMargins(
            14,
            14,
            14,
            14,
        )

        root_layout.setSpacing(
            12
        )

        root_layout.addWidget(
            self._build_header()
        )

        content = QHBoxLayout()

        content.setSpacing(
            12
        )

        content.addWidget(
            self._build_sidebar()
        )

        content.addWidget(
            self._build_center(),
            1,
        )

        content.addWidget(
            self._build_right_panel()
        )

        root_layout.addLayout(
            content,
            1,
        )

        self.setCentralWidget(
            root
        )

    def _build_header(
        self,
    ) -> QWidget:

        header = QFrame()

        header.setObjectName(
            "header"
        )

        layout = QHBoxLayout(
            header
        )

        layout.setContentsMargins(
            18,
            9,
            18,
            9,
        )

        left = QVBoxLayout()

        left.setSpacing(
            0
        )

        brand = QLabel(
            "J . A . R . V . I . S ."
        )

        brand.setObjectName(
            "brand"
        )

        subtitle = QLabel(
            "JUST A RATHER VERY INTELLIGENT SYSTEM"
        )

        subtitle.setObjectName(
            "brandSubtitle"
        )

        left.addWidget(
            brand
        )

        left.addWidget(
            subtitle
        )

        layout.addLayout(
            left
        )

        version = QLabel(
            "SYS BUILD 0.1 ALPHA"
        )

        version.setObjectName(
            "version"
        )

        layout.addSpacing(
            20
        )

        layout.addWidget(
            version
        )

        layout.addStretch()

        self.header_status = QLabel(
            "SYS-CORE  //  INITIALIZING"
        )

        self.header_status.setObjectName(
            "headerStatus"
        )

        layout.addWidget(
            self.header_status
        )

        layout.addSpacing(
            16
        )

        profile = QLabel(
            "USER // RICCARDO"
        )

        profile.setObjectName(
            "profile"
        )

        layout.addWidget(
            profile
        )

        return header

    def _build_sidebar(
        self,
    ) -> QWidget:

        panel = QFrame()

        panel.setObjectName(
            "sidePanel"
        )

        panel.setFixedWidth(
            210
        )

        layout = QVBoxLayout(
            panel
        )

        layout.setContentsMargins(
            12,
            16,
            12,
            16,
        )

        layout.setSpacing(
            6
        )

        section = QLabel(
            "NAVIGATION"
        )

        section.setObjectName(
            "tinyTitle"
        )

        layout.addWidget(
            section
        )

        nav_items = [
            ("CHAT", "Conversazione"),
            ("VOICE", "Controllo vocale"),
            ("MEMORY", "Memoria"),
            ("PROJECTS", "Progetti"),
            ("TOOLS", "Strumenti"),
            ("SYSTEM", "Computer"),
            ("AUTOMATION", "Workflow"),
        ]

        for index, (
            title,
            subtitle,
        ) in enumerate(
            nav_items
        ):
            button = QPushButton(
                f"{title}\n{subtitle}"
            )

            button.setObjectName(
                "navActive"
                if index == 0
                else "navButton"
            )

            button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

            layout.addWidget(
                button
            )

        layout.addStretch()

        separator = QFrame()

        separator.setFrameShape(
            QFrame.Shape.HLine
        )

        separator.setObjectName(
            "separator"
        )

        layout.addWidget(
            separator
        )

        identity = QLabel(
            "JARVIS DESKTOP CORE\n"
            "LOCAL AI SYSTEM\n"
            "SECURE SESSION"
        )

        identity.setObjectName(
            "identity"
        )

        layout.addWidget(
            identity
        )

        return panel

    def _build_center(
        self,
    ) -> QWidget:

        panel = QFrame()

        panel.setObjectName(
            "centerPanel"
        )

        layout = QVBoxLayout(
            panel
        )

        layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        layout.setSpacing(
            10
        )

        top = QHBoxLayout()

        titles = QVBoxLayout()

        titles.setSpacing(
            1
        )

        title = QLabel(
            "CONVERSATION CORE"
        )

        title.setObjectName(
            "sectionTitle"
        )

        subtitle = QLabel(
            "REAL-TIME NATURAL LANGUAGE INTERFACE"
        )

        subtitle.setObjectName(
            "sectionSubtitle"
        )

        titles.addWidget(
            title
        )

        titles.addWidget(
            subtitle
        )

        top.addLayout(
            titles
        )

        top.addStretch()

        self.center_status = QLabel(
            "● STARTING"
        )

        self.center_status.setObjectName(
            "centerStatus"
        )

        top.addWidget(
            self.center_status
        )

        layout.addLayout(
            top
        )

        tech_line = QFrame()

        tech_line.setFrameShape(
            QFrame.Shape.HLine
        )

        tech_line.setObjectName(
            "separator"
        )

        layout.addWidget(
            tech_line
        )

        middle = QHBoxLayout()

        middle.setSpacing(
            10
        )

        chat_frame = QFrame()

        chat_frame.setObjectName(
            "chatFrame"
        )

        chat_layout = QVBoxLayout(
            chat_frame
        )

        chat_layout.setContentsMargins(
            12,
            10,
            12,
            10,
        )

        chat_header = QLabel(
            "DATA STREAM // CHAT SESSION"
        )

        chat_header.setObjectName(
            "tinyTitle"
        )

        self.chat = QTextEdit()

        self.chat.setObjectName(
            "chat"
        )

        self.chat.setReadOnly(
            True
        )

        self.chat.setPlaceholderText(
            "Awaiting input..."
        )

        chat_layout.addWidget(
            chat_header
        )

        chat_layout.addWidget(
            self.chat,
            1,
        )

        middle.addWidget(
            chat_frame,
            3,
        )

        core_frame = QFrame()

        core_frame.setObjectName(
            "coreFrame"
        )

        core_layout = QVBoxLayout(
            core_frame
        )

        core_layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )

        core_layout.setSpacing(
            6
        )

        core_header = QLabel(
            "AI CORE // ACTIVE MATRIX"
        )

        core_header.setObjectName(
            "tinyTitle"
        )

        core_header.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.orb = JarvisOrb()

        self.orb_status = QLabel(
            "INITIALIZING"
        )

        self.orb_status.setObjectName(
            "orbStatus"
        )

        self.orb_status.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        core_substatus = QLabel(
            "NEURAL LINK // STANDBY"
        )

        core_substatus.setObjectName(
            "coreSubstatus"
        )

        core_substatus.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        core_layout.addWidget(
            core_header
        )

        core_layout.addStretch()

        core_layout.addWidget(
            self.orb
        )

        core_layout.addWidget(
            self.orb_status
        )

        core_layout.addWidget(
            core_substatus
        )

        core_layout.addStretch()

        middle.addWidget(
            core_frame,
            2,
        )

        layout.addLayout(
            middle,
            1,
        )

        composer = QFrame()

        composer.setObjectName(
            "composer"
        )

        composer_layout = QHBoxLayout(
            composer
        )

        composer_layout.setContentsMargins(
            8,
            6,
            8,
            6,
        )

        self.command_input = QLineEdit()

        self.command_input.setPlaceholderText(
            "Input command..."
        )

        self.microphone_button = QPushButton(
            "VOICE"
        )

        self.microphone_button.setObjectName(
            "actionButton"
        )

        self.stop_button = QPushButton(
            "ABORT"
        )

        self.stop_button.setObjectName(
            "stopButton"
        )

        self.send_button = QPushButton(
            "SEND"
        )

        self.send_button.setObjectName(
            "actionButton"
        )

        composer_layout.addWidget(
            self.command_input,
            1,
        )

        composer_layout.addWidget(
            self.microphone_button
        )

        composer_layout.addWidget(
            self.stop_button
        )

        composer_layout.addWidget(
            self.send_button
        )

        layout.addWidget(
            composer
        )

        footer = QLabel(
            "THINK // PLAN // EXECUTE // ADAPT"
        )

        footer.setObjectName(
            "footer"
        )

        footer.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            footer
        )

        return panel

    def _build_right_panel(
        self,
    ) -> QWidget:

        panel = QFrame()

        panel.setObjectName(
            "rightPanel"
        )

        panel.setFixedWidth(
            280
        )

        layout = QVBoxLayout(
            panel
        )

        layout.setContentsMargins(
            10,
            12,
            10,
            12,
        )

        layout.setSpacing(
            8
        )

        title = QLabel(
            "SYSTEM TELEMETRY"
        )

        title.setObjectName(
            "tinyTitle"
        )

        layout.addWidget(
            title
        )

        self.system_card = InfoCard(
            "SYS-01 // SYSTEM",
            "Initializing...",
        )

        self.ai_card = InfoCard(
            "AI-CORE // OLLAMA",
            "Connection pending",
        )

        self.voice_card = InfoCard(
            "VOICE-LINK",
            "Microphone: pending\n"
            "Wake Word: pending",
        )

        self.modules_card = InfoCard(
            "MODULE MATRIX",
            "AI Core\n"
            "Voice Engine\n"
            "Memory\n"
            "Computer Control\n"
            "Wake Word",
        )

        self.security_card = InfoCard(
            "SESSION",
            "LOCAL MODE\n"
            "USER: RICCARDO\n"
            "BUILD: 0.1 ALPHA",
        )

        layout.addWidget(
            self.system_card
        )

        layout.addWidget(
            self.ai_card
        )

        layout.addWidget(
            self.voice_card
        )

        layout.addWidget(
            self.modules_card
        )

        layout.addWidget(
            self.security_card
        )

        layout.addStretch()

        return panel

    def _apply_style(
        self,
    ) -> None:

        self.setStyleSheet(
            """
            QWidget {
                color: #D7EDF7;
                font-family: "Segoe UI";
            }

            QFrame#header,
            QFrame#sidePanel,
            QFrame#centerPanel,
            QFrame#rightPanel {
                background-color: rgba(3, 12, 20, 220);
                border: 1px solid rgba(25, 111, 158, 105);
                border-radius: 6px;
            }

            QFrame#header {
                border-bottom: 1px solid #078CCF;
            }

            QLabel#brand {
                color: #F4FCFF;
                font-size: 24px;
                font-weight: 600;
                letter-spacing: 5px;
            }

            QLabel#brandSubtitle {
                color: #4D91B3;
                font-size: 8px;
                letter-spacing: 3px;
            }

            QLabel#version {
                color: #00B8E6;
                font-size: 9px;
                border-left: 1px solid #15506B;
                padding-left: 18px;
            }

            QLabel#headerStatus {
                color: #61CFF3;
                font-size: 9px;
                letter-spacing: 1px;
            }

            QLabel#profile {
                color: #9EC7D9;
                font-size: 10px;
            }

            QLabel#tinyTitle {
                color: #367E9F;
                font-size: 8px;
                font-weight: 600;
                letter-spacing: 2px;
            }

            QPushButton#navButton,
            QPushButton#navActive {
                text-align: left;
                min-height: 42px;
                padding-left: 13px;
                border-radius: 3px;
                font-size: 10px;
            }

            QPushButton#navButton {
                color: #668EA1;
                background-color: transparent;
                border: 1px solid transparent;
            }

            QPushButton#navButton:hover {
                color: #CBEFFF;
                background-color: rgba(0, 109, 160, 20);
                border-left: 2px solid #0088C8;
            }

            QPushButton#navActive {
                color: #DFF8FF;
                background-color: rgba(0, 105, 155, 28);
                border: 1px solid rgba(0, 145, 210, 85);
                border-left: 2px solid #00BFFF;
            }

            QLabel#identity {
                color: #315E73;
                font-size: 8px;
                letter-spacing: 2px;
                line-height: 150%;
            }

            QLabel#sectionTitle {
                color: #E8F8FF;
                font-size: 15px;
                font-weight: 600;
                letter-spacing: 1px;
            }

            QLabel#sectionSubtitle {
                color: #3F7893;
                font-size: 8px;
                letter-spacing: 1px;
            }

            QLabel#centerStatus {
                color: #00E59B;
                background-color: rgba(0, 40, 40, 120);
                border: 1px solid #106E63;
                border-radius: 3px;
                padding: 5px 9px;
                font-size: 9px;
                font-weight: 600;
                letter-spacing: 1px;
            }

            QFrame#chatFrame,
            QFrame#coreFrame {
                background-color: rgba(0, 5, 10, 185);
                border: 1px solid rgba(25, 93, 125, 85);
                border-radius: 4px;
            }

            QTextEdit#chat {
                background-color: rgba(0, 4, 8, 155);
                border: none;
                color: #CDE8F4;
                font-size: 13px;
                padding: 8px;
                selection-background-color: #075F89;
            }

            QFrame#composer {
                background-color: rgba(3, 14, 22, 220);
                border: 1px solid #164A62;
                border-radius: 4px;
            }

            QLineEdit {
                background-color: transparent;
                color: #DDF7FF;
                border: none;
                padding: 9px;
                font-size: 12px;
            }

            QLineEdit::placeholder {
                color: #3D7188;
            }

            QPushButton#actionButton {
                min-width: 58px;
                min-height: 34px;
                color: #BDEBFF;
                background-color: rgba(0, 80, 120, 45);
                border: 1px solid #17658A;
                border-radius: 3px;
                font-size: 9px;
                font-weight: 600;
            }

            QPushButton#actionButton:hover {
                color: white;
                background-color: rgba(0, 130, 190, 75);
                border: 1px solid #00B8F0;
            }

            QPushButton#stopButton {
                min-width: 58px;
                min-height: 34px;
                color: #DF8898;
                background-color: rgba(90, 10, 30, 55);
                border: 1px solid #813348;
                border-radius: 3px;
                font-size: 9px;
                font-weight: 600;
            }

            QPushButton#stopButton:hover {
                color: #FFD7DE;
                border: 1px solid #D94A68;
                background-color: rgba(120, 18, 42, 80);
            }

            QLabel#orbStatus {
                color: #00CFFF;
                font-size: 10px;
                font-weight: 600;
                letter-spacing: 4px;
            }

            QLabel#coreSubstatus {
                color: #356B83;
                font-size: 8px;
                letter-spacing: 2px;
            }

            QLabel#footer {
                color: #214F64;
                font-size: 8px;
                letter-spacing: 4px;
            }

            QFrame#infoCard {
                background-color: rgba(4, 16, 25, 190);
                border: 1px solid rgba(16, 83, 116, 90);
                border-radius: 4px;
            }

            QLabel#cardTitle {
                color: #4FA8CD;
                font-size: 8px;
                font-weight: 600;
                letter-spacing: 1px;
            }

            QLabel#cardValue {
                color: #AFCFDC;
                font-size: 10px;
            }

            QFrame#separator {
                color: rgba(30, 100, 130, 90);
            }

            QScrollBar:vertical {
                background: #02080D;
                width: 7px;
            }

            QScrollBar::handle:vertical {
                background: #0D4C68;
                min-height: 24px;
            }

            QScrollBar::handle:vertical:hover {
                background: #14739B;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            """
        )

    def _connect_signals(
        self,
    ) -> None:

        self.send_button.clicked.connect(
            self._send_command
        )

        self.command_input.returnPressed.connect(
            self._send_command
        )

        self.microphone_button.clicked.connect(
            self._listen_microphone
        )

        self.stop_button.clicked.connect(
            self._stop_response
        )

        self.conversation_event.connect(
            self._handle_conversation_event
        )

        self.startup_finished.connect(
            self._handle_startup_finished
        )

        self.command_finished.connect(
            self._handle_command_finished
        )

        self.microphone_result.connect(
            self._handle_microphone_result
        )

        self.startup_error.connect(
            self._handle_startup_error
        )

    def _start_assistant(
        self,
    ) -> None:

        def worker() -> None:
            try:
                self._assistant.start()

                self.startup_finished.emit()

            except Exception as error:
                self.startup_error.emit(
                    str(error)
                )

        threading.Thread(
            target=worker,
            daemon=True,
        ).start()

    def _handle_startup_finished(
        self,
    ) -> None:

        self.system_card.set_value(
            "● ONLINE\n"
            "Core services initialized"
        )

        self.ai_card.set_value(
            "● OLLAMA ONLINE\n"
            "Local inference ready"
        )

        self.voice_card.set_value(
            "Microphone: ONLINE\n"
            "Wake Word: ACTIVE"
        )

        self._interrupt_listener = (
            InterruptListener(
                logger=(
                    self._assistant
                    .services
                    .logger
                ),
                cancel_callback=(
                    self._assistant
                    .conversation
                    .cancel_current_response
                ),
            )
        )

        self._interrupt_listener.start()

        self._background_wake = (
            BackgroundWakeListener(
                assistant=self._assistant
            )
        )

        self._background_wake.start()

        self._set_controls_enabled(
            True
        )

        self._set_state(
            JarvisState.READY
        )

    def _handle_startup_error(
        self,
        error: str,
    ) -> None:

        self.chat.append(
            "<b style='color:#FF5470;'>"
            "SYSTEM ERROR // "
            "</b>"
            f"{error}"
        )

        self.system_card.set_value(
            "● SYSTEM ERROR"
        )

        self._set_state(
            JarvisState.ERROR
        )

    def _send_command(
        self,
    ) -> None:

        if self._busy:
            return

        command = (
            self.command_input
            .text()
            .strip()
        )

        if not command:
            return

        self.command_input.clear()

        self.chat.append(
            "<br>"
            "<span style='color:#5F8DA2;'>"
            "USER // RICCARDO"
            "</span>"
            "<br>"
            "<span style='color:#E0F4FC;'>"
            f"{command}"
            "</span>"
            "<br>"
        )

        self._process_command(
            command
        )

    def _process_command(
        self,
        command: str,
    ) -> None:

        self._busy = True

        self._set_controls_enabled(
            False
        )

        self.stop_button.setEnabled(
            True
        )

        self._set_state(
            JarvisState.THINKING
        )

        def worker() -> None:
            try:
                self._assistant.process_command(
                    command
                )

            except Exception as error:
                self.conversation_event.emit(
                    "error",
                    str(error),
                )

            finally:
                self.command_finished.emit()

        threading.Thread(
            target=worker,
            daemon=True,
        ).start()

    def _handle_command_finished(
        self,
    ) -> None:

        self._busy = False

        self._set_controls_enabled(
            True
        )

        self._set_state(
            JarvisState.READY
        )

    def _listen_microphone(
        self,
    ) -> None:

        if self._busy:
            return

        self._busy = True

        self._set_controls_enabled(
            False
        )

        self._set_state(
            JarvisState.LISTENING
        )

        def worker() -> None:

            command = (
                self._assistant
                .services
                .audio
                .listen(
                    timeout_seconds=8.0
                )
            )

            self.microphone_result.emit(
                command
            )

        threading.Thread(
            target=worker,
            daemon=True,
        ).start()

    def _handle_microphone_result(
        self,
        command: str,
    ) -> None:

        self._busy = False

        if not command.strip():

            self._set_controls_enabled(
                True
            )

            self._set_state(
                JarvisState.READY
            )

            return

        self.chat.append(
            "<br>"
            "<span style='color:#5F8DA2;'>"
            "VOICE INPUT // RICCARDO"
            "</span>"
            "<br>"
            f"{command}"
            "<br>"
        )

        self._process_command(
            command
        )

    def _stop_response(
        self,
    ) -> None:

        stopped = (
            self._assistant
            .conversation
            .cancel_current_response()
        )

        if stopped:

            self.chat.append(
                "<br>"
                "<span style='color:#D94A68;'>"
                "SYSTEM // RESPONSE ABORTED"
                "</span>"
            )

            self._set_state(
                JarvisState.READY
            )

    def _conversation_callback(
        self,
        event: str,
        text: str,
    ) -> None:

        self.conversation_event.emit(
            event,
            text,
        )

    def _handle_conversation_event(
        self,
        event: str,
        text: str,
    ) -> None:

        if event == "message":

            self.chat.append(
                "<br>"
                "<span style='color:#00CFFF;'>"
                "J.A.R.V.I.S. // RESPONSE"
                "</span>"
                "<br>"
                f"{text}"
                "<br>"
            )

            self._set_state(
                JarvisState.SPEAKING
            )

        elif event == "stream_start":

            self.chat.append(
                "<br>"
                "<span style='color:#00CFFF;'>"
                "J.A.R.V.I.S. // STREAM"
                "</span>"
                "<br>"
            )

            self._set_state(
                JarvisState.SPEAKING
            )

        elif event == "stream_chunk":

            cursor = (
                self.chat
                .textCursor()
            )

            cursor.movePosition(
                cursor.MoveOperation.End
            )

            cursor.insertText(
                text
            )

            self.chat.setTextCursor(
                cursor
            )

            self.chat.ensureCursorVisible()

        elif event == "error":

            self.chat.append(
                "<br>"
                "<span style='color:#FF5470;'>"
                "ERROR // "
                "</span>"
                f"{text}"
            )

            self._set_state(
                JarvisState.ERROR
            )

    def _set_state(
        self,
        state: JarvisState,
    ) -> None:

        label = (
            StatusManager.label(
                state
            )
        )

        color = (
            StatusManager.color(
                state
            )
        )

        self.center_status.setText(
            f"● {label}"
        )

        self.center_status.setStyleSheet(
            f"""
            color: {color};
            background-color: rgba(0, 15, 24, 190);
            border: 1px solid {color};
            border-radius: 3px;
            padding: 5px 9px;
            font-size: 9px;
            font-weight: 600;
            letter-spacing: 1px;
            """
        )

        self.header_status.setText(
            f"SYS-CORE // {label}"
        )

        self.header_status.setStyleSheet(
            f"color: {color};"
        )

        self.orb_status.setText(
            label
        )

        self.orb_status.setStyleSheet(
            f"""
            color: {color};
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 4px;
            """
        )

        if state == JarvisState.READY:
            self.orb.set_activity(
                0.35
            )

        elif state == JarvisState.LISTENING:
            self.orb.set_activity(
                0.85
            )

        elif state == JarvisState.THINKING:
            self.orb.set_activity(
                1.7
            )

        elif state == JarvisState.SPEAKING:
            self.orb.set_activity(
                1.15
            )

        elif state == JarvisState.ERROR:
            self.orb.set_activity(
                0.2
            )

        else:
            self.orb.set_activity(
                0.6
            )

        self.state_changed.emit(
            state
        )

    def _set_controls_enabled(
        self,
        enabled: bool,
    ) -> None:

        self.command_input.setEnabled(
            enabled
        )

        self.send_button.setEnabled(
            enabled
        )

        self.microphone_button.setEnabled(
            enabled
        )

        self.stop_button.setEnabled(
            True
        )

    def shutdown_and_close(
        self,
    ) -> None:

        self._allow_close = True

        try:
            self._assistant.conversation.cancel_current_response()

            if self._background_wake is not None:
                self._background_wake.stop()

            if self._interrupt_listener is not None:
                self._interrupt_listener.stop()

            self._assistant.shutdown()

        except Exception:
            pass

        self.close()

    def closeEvent(
        self,
        event,
    ) -> None:

        if self._allow_close:
            event.accept()

            return

        self.hide()

        event.ignore()