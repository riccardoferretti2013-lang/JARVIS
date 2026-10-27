import threading

from datetime import datetime

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)

from ..audio.interrupt_listener import InterruptListener
from ..core.assistant import Assistant
from ..gui.background_wake import BackgroundWakeListener
from .system_monitor import SystemMonitor


class JarvisBridge(QObject):

    # ============================================================
    # GENERAL SIGNALS
    # ============================================================

    stateChanged = Signal(
        str,
        str,
    )

    audioLevelChanged = Signal(
        str,
        float,
    )

    assistantMessage = Signal(
        str
    )

    streamStarted = Signal()

    streamChunk = Signal(
        str
    )

    streamFinished = Signal()

    voiceCommandDetected = Signal(
        str
    )

    readyChanged = Signal(
        bool
    )

    errorOccurred = Signal(
        str
    )

    shutdownFinished = Signal()

    telemetryChanged = Signal(
        float,
        float,
        float,
        float,
        float,
        float,
        str,
    )

    # ============================================================
    # GUI NAVIGATION
    # ============================================================

    pageRequested = Signal(
        str
    )

    # ============================================================
    # MEMORY
    # ============================================================

    memoryDataChanged = Signal(
        list,
        int,
        int,
    )

    memoryOperationCompleted = Signal(
        str,
        bool,
        str,
    )

    # ============================================================
    # INIT
    # ============================================================

    def __init__(
        self,
        assistant: Assistant,
    ) -> None:

        super().__init__()

        self._assistant = assistant

        self._busy = False
        self._ready = False

        self._interrupt_listener = None
        self._background_wake = None

        self._system_monitor = (
            SystemMonitor()
        )

        self._system_monitor.telemetryUpdated.connect(
            self.telemetryChanged.emit
        )

        self._assistant.conversation.set_output_callback(
            self._conversation_callback
        )

        self._assistant.services.audio.set_audio_level_callback(
            self._audio_level_callback
        )

    # ============================================================
    # MEMORY SERVICE
    # ============================================================

    @property
    def _memory_service(self):
        """
        Restituisce il MemoryService realmente usato
        dal motore AI di J.A.R.V.I.S.
        """

        return (
            self._assistant
            .agent
            .ai
            .memory_service
        )

    # ============================================================
    # START
    # ============================================================

    @Slot()
    def start(
        self,
    ) -> None:

        if self._ready:
            return

        self._set_state(
            "STARTING",
            "#FFC857",
        )

        self._system_monitor.start()

        threading.Thread(
            target=self._startup_worker,
            daemon=True,
            name="JarvisStartup",
        ).start()

    def _startup_worker(
        self,
    ) -> None:

        try:

            self._assistant.start()

            self._assistant.services.audio.set_audio_level_callback(
                self._audio_level_callback
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

            self._ready = True

            self.readyChanged.emit(
                True
            )

            self._set_state(
                "READY",
                "#00E59B",
            )

            self._emit_memory_data()

        except Exception as error:

            self._ready = False

            self.readyChanged.emit(
                False
            )

            self._set_state(
                "ERROR",
                "#FF4D6D",
            )

            self.errorOccurred.emit(
                str(error)
            )

    # ============================================================
    # LOCAL GUI COMMANDS
    # ============================================================

    def _handle_local_gui_command(
        self,
        command: str,
    ) -> bool:
        """
        Intercetta i comandi che riguardano esclusivamente
        l'interfaccia grafica.

        Questi comandi NON vengono inviati a OpenAI
        e NON consumano richieste API.
        """

        normalized = (
            command
            .strip()
            .lower()
            .replace("’", "'")
            .replace("`", "'")
        )

        company_commands = (
            "fammi vedere l'azienda",
            "fammi vedere azienda",
            "apri l'azienda",
            "apri azienda",
            "mostrami l'azienda",
            "mostrami azienda",
            "fammi vedere la ai company",
            "fammi vedere ai company",
            "apri la ai company",
            "apri ai company",
            "mostrami la ai company",
            "mostrami ai company",
            "fammi vedere la company",
            "apri la company",
            "mostrami la company",
        )

        if any(
            phrase in normalized
            for phrase in company_commands
        ):

            self.pageRequested.emit(
                "company"
            )

            self.assistantMessage.emit(
                "Apro la AI Company."
            )

            return True

        return False

    # ============================================================
    # TEXT COMMAND
    # ============================================================

    @Slot(str)
    def sendCommand(
        self,
        command: str,
    ) -> None:

        command = command.strip()

        if (
            not command
            or self._busy
            or not self._ready
        ):
            return

        # --------------------------------------------------------
        # LOCAL GUI COMMAND
        # --------------------------------------------------------

        if self._handle_local_gui_command(
            command
        ):
            return

        self._busy = True

        self._set_state(
            "THINKING",
            "#8B7CFF",
        )

        threading.Thread(
            target=self._command_worker,
            args=(command,),
            daemon=True,
            name="JarvisCommand",
        ).start()

    def _command_worker(
        self,
        command: str,
    ) -> None:

        try:

            self._assistant.process_command(
                command
            )

        except Exception as error:

            self.errorOccurred.emit(
                str(error)
            )

            self._set_state(
                "ERROR",
                "#FF4D6D",
            )

        finally:

            self._busy = False

            self._emit_memory_data()

            if self._ready:

                self._set_state(
                    "READY",
                    "#00E59B",
                )

    # ============================================================
    # MICROPHONE
    # ============================================================

    @Slot()
    def listenMicrophone(
        self,
    ) -> None:

        if (
            self._busy
            or not self._ready
        ):
            return

        self._busy = True

        self._set_state(
            "LISTENING",
            "#00E5FF",
        )

        threading.Thread(
            target=self._microphone_worker,
            daemon=True,
            name="JarvisMicrophone",
        ).start()

    def _microphone_worker(
        self,
    ) -> None:

        try:

            command = (
                self._assistant
                .services
                .audio
                .listen(
                    timeout_seconds=8.0
                )
            )

            command = (
                command.strip()
            )

            if not command:
                return

            self.voiceCommandDetected.emit(
                command
            )

            # ----------------------------------------------------
            # LOCAL GUI COMMAND
            # ----------------------------------------------------

            if self._handle_local_gui_command(
                command
            ):
                return

            self._set_state(
                "THINKING",
                "#8B7CFF",
            )

            self._assistant.process_command(
                command
            )

        except Exception as error:

            self.errorOccurred.emit(
                str(error)
            )

        finally:

            self._busy = False

            self.audioLevelChanged.emit(
                "input",
                0.0,
            )

            self._emit_memory_data()

            if self._ready:

                self._set_state(
                    "READY",
                    "#00E59B",
                )

    # ============================================================
    # STOP RESPONSE
    # ============================================================

    @Slot()
    def stopResponse(
        self,
    ) -> None:

        stopped = (
            self._assistant
            .conversation
            .cancel_current_response()
        )

        if stopped:

            self._busy = False

            self.audioLevelChanged.emit(
                "output",
                0.0,
            )

            self._set_state(
                "READY",
                "#00E59B",
            )

    # ============================================================
    # MEMORY - LOAD
    # ============================================================

    @Slot()
    def loadMemory(
        self,
    ) -> None:

        threading.Thread(
            target=self._load_memory_worker,
            daemon=True,
            name="JarvisMemoryLoad",
        ).start()

    def _load_memory_worker(
        self,
    ) -> None:

        try:

            self._emit_memory_data()

            self.memoryOperationCompleted.emit(
                "load",
                True,
                "Memoria aggiornata.",
            )

        except Exception as error:

            self.memoryOperationCompleted.emit(
                "load",
                False,
                str(error),
            )

            self.errorOccurred.emit(
                f"Errore caricamento memoria: {error}"
            )

    # ============================================================
    # MEMORY - DELETE
    # ============================================================

    @Slot(int)
    def deleteMemory(
        self,
        memory_id: int,
    ) -> None:

        if memory_id < 0:
            return

        threading.Thread(
            target=self._delete_memory_worker,
            args=(memory_id,),
            daemon=True,
            name="JarvisMemoryDelete",
        ).start()

    def _delete_memory_worker(
        self,
        memory_id: int,
    ) -> None:

        try:

            deleted = (
                self._memory_service
                .forget(
                    memory_id
                )
            )

            if deleted:

                self.memoryOperationCompleted.emit(
                    "delete",
                    True,
                    "Ricordo eliminato.",
                )

            else:

                self.memoryOperationCompleted.emit(
                    "delete",
                    False,
                    "Ricordo non trovato.",
                )

            self._emit_memory_data()

        except Exception as error:

            self.memoryOperationCompleted.emit(
                "delete",
                False,
                str(error),
            )

            self.errorOccurred.emit(
                f"Errore eliminazione memoria: {error}"
            )

    # ============================================================
    # MEMORY - REBUILD SEMANTIC INDEX
    # ============================================================

    @Slot()
    def rebuildMemoryIndex(
        self,
    ) -> None:

        threading.Thread(
            target=self._rebuild_memory_index_worker,
            daemon=True,
            name="JarvisMemoryRebuild",
        ).start()

    def _rebuild_memory_index_worker(
        self,
    ) -> None:

        try:

            indexed_count = (
                self._memory_service
                .rebuild_semantic_index()
            )

            self.memoryOperationCompleted.emit(
                "rebuild",
                True,
                (
                    "Indice semantico ricostruito: "
                    f"{indexed_count} ricordi."
                ),
            )

            self._emit_memory_data()

        except Exception as error:

            self.memoryOperationCompleted.emit(
                "rebuild",
                False,
                str(error),
            )

            self.errorOccurred.emit(
                (
                    "Errore ricostruzione "
                    f"indice memoria: {error}"
                )
            )

    # ============================================================
    # MEMORY - CLEAR
    # ============================================================

    @Slot()
    def clearMemory(
        self,
    ) -> None:

        threading.Thread(
            target=self._clear_memory_worker,
            daemon=True,
            name="JarvisMemoryClear",
        ).start()

    def _clear_memory_worker(
        self,
    ) -> None:

        try:

            self._memory_service.clear()

            self.memoryOperationCompleted.emit(
                "clear",
                True,
                "Memoria permanente svuotata.",
            )

            self._emit_memory_data()

        except Exception as error:

            self.memoryOperationCompleted.emit(
                "clear",
                False,
                str(error),
            )

            self.errorOccurred.emit(
                f"Errore cancellazione memoria: {error}"
            )

    # ============================================================
    # MEMORY - SEND DATA TO QML
    # ============================================================

    def _emit_memory_data(
        self,
    ) -> None:

        memory_service = (
            self._memory_service
        )

        memories = list(
            memory_service
            .get_all_memories()
        )

        memories.sort(
            key=self._memory_sort_key,
            reverse=True,
        )

        serialized_memories = [
            self._serialize_memory(
                memory
            )
            for memory in memories
        ]

        total_count = (
            memory_service.count()
        )

        try:

            semantic_count = (
                memory_service
                .semantic_count()
            )

        except RuntimeError:

            semantic_count = 0

        self.memoryDataChanged.emit(
            serialized_memories,
            total_count,
            semantic_count,
        )

    @staticmethod
    def _memory_sort_key(
        memory,
    ) -> datetime:

        return (
            memory.updated_at
            or memory.created_at
            or datetime.min
        )

    @staticmethod
    def _serialize_datetime(
        value: datetime | None,
    ) -> str:

        if value is None:
            return "--"

        return value.strftime(
            "%d/%m/%Y %H:%M"
        )

    @classmethod
    def _serialize_memory(
        cls,
        memory,
    ) -> dict:

        memory_type = getattr(
            memory.memory_type,
            "value",
            str(memory.memory_type),
        )

        memory_id = (
            memory.memory_id
            if memory.memory_id is not None
            else -1
        )

        return {
            "memoryId": int(
                memory_id
            ),

            "key": str(
                memory.key
            ),

            "value": str(
                memory.value
            ),

            "memoryType": str(
                memory_type
            ),

            "importance": int(
                memory.importance
            ),

            "createdAt": (
                cls._serialize_datetime(
                    memory.created_at
                )
            ),

            "updatedAt": (
                cls._serialize_datetime(
                    memory.updated_at
                )
            ),
        }

    # ============================================================
    # SHUTDOWN
    # ============================================================

    @Slot()
    def shutdown(
        self,
    ) -> None:

        threading.Thread(
            target=self._shutdown_worker,
            daemon=True,
            name="JarvisShutdown",
        ).start()

    def _shutdown_worker(
        self,
    ) -> None:

        try:

            self._system_monitor.stop()

            self._assistant.conversation.cancel_current_response()

            if self._background_wake is not None:

                self._background_wake.stop()

            if self._interrupt_listener is not None:

                self._interrupt_listener.stop()

            self._assistant.shutdown()

        finally:

            self._ready = False

            self.shutdownFinished.emit()

    # ============================================================
    # AUDIO CALLBACK
    # ============================================================

    def _audio_level_callback(
        self,
        source: str,
        level: float,
    ) -> None:

        self.audioLevelChanged.emit(
            source,
            level,
        )

    # ============================================================
    # CONVERSATION CALLBACK
    # ============================================================

    def _conversation_callback(
        self,
        event: str,
        text: str,
    ) -> None:

        if event == "message":

            self._set_state(
                "SPEAKING",
                "#00A8FF",
            )

            self.assistantMessage.emit(
                text
            )

        elif event == "stream_start":

            self._set_state(
                "SPEAKING",
                "#00A8FF",
            )

            self.streamStarted.emit()

        elif event == "stream_chunk":

            self.streamChunk.emit(
                text
            )

        elif event == "stream_end":

            self.streamFinished.emit()

    # ============================================================
    # STATE
    # ============================================================

    def _set_state(
        self,
        state: str,
        color: str,
    ) -> None:

        self.stateChanged.emit(
            state,
            color,
        )