from collections.abc import Callable

from ..config.settings_manager import SettingsManager
from ..services.base_service import BaseService
from ..services.logger_service import LoggerService

from .input.microphone import Microphone
from .input.speech_to_text import SpeechToText
from .output.voice_manager import VoiceManager


AudioLevelCallback = Callable[
    [str, float],
    None,
]


class AudioEngine(BaseService):

    def __init__(
        self,
        settings: SettingsManager,
        logger: LoggerService,
    ) -> None:

        super().__init__(
            "Audio Engine"
        )

        self._settings = settings
        self._logger = logger

        self._microphone: (
            Microphone | None
        ) = None

        self._speech_to_text: (
            SpeechToText | None
        ) = None

        self._voice_manager: (
            VoiceManager | None
        ) = None

        self._audio_level_callback: (
            AudioLevelCallback | None
        ) = None

    @property
    def is_speaking(
        self,
    ) -> bool:

        if self._voice_manager is None:
            return False

        return (
            self._voice_manager
            .is_speaking
        )

    def set_audio_level_callback(
        self,
        callback: AudioLevelCallback | None,
    ) -> None:

        self._audio_level_callback = (
            callback
        )

        if self._microphone is not None:

            self._microphone.set_audio_level_callback(
                self._handle_input_level
            )

        if self._voice_manager is not None:

            self._voice_manager.set_audio_level_callback(
                self._handle_output_level
            )

    def initialize(
        self,
    ) -> None:

        if self.initialized:
            return

        self._logger.info(
            "Inizializzazione Audio Engine."
        )

        self._microphone = (
            Microphone(
                audio_level_callback=(
                    self._handle_input_level
                )
            )
        )

        self._speech_to_text = (
            SpeechToText(
                settings=self._settings,
                logger=self._logger,
            )
        )

        self._voice_manager = (
            VoiceManager(
                settings=self._settings,
                logger=self._logger,
                audio_level_callback=(
                    self._handle_output_level
                ),
            )
        )

        super().initialize()

        self._logger.info(
            "Audio Engine inizializzato."
        )

    def shutdown(
        self,
    ) -> None:

        if not self.initialized:
            return

        self._logger.info(
            "Arresto Audio Engine."
        )

        if (
            self._voice_manager
            is not None
        ):

            try:
                self._voice_manager.stop()

            except Exception:
                pass

        self._emit_audio_level(
            "input",
            0.0,
        )

        self._emit_audio_level(
            "output",
            0.0,
        )

        self._microphone = None
        self._speech_to_text = None
        self._voice_manager = None

        super().shutdown()

    def listen(
        self,
        timeout_seconds: float | None = None,
    ) -> str:

        if not self.initialized:

            raise RuntimeError(
                "Audio Engine non inizializzato."
            )

        if (
            self._microphone is None
            or self._speech_to_text
            is None
        ):

            raise RuntimeError(
                "Componenti audio non disponibili."
            )

        try:

            audio_file = (
                self._microphone.record(
                    timeout_seconds=(
                        timeout_seconds
                    )
                )
            )

            if not audio_file:

                self._logger.info(
                    "Timeout microfono raggiunto."
                )

                return ""

            transcription = (
                self._speech_to_text
                .transcribe(
                    audio_file
                )
            )

            return (
                transcription.strip()
            )

        except Exception as error:

            self._logger.error(
                "Errore durante l'ascolto: "
                f"{error}"
            )

            return ""

        finally:

            self._emit_audio_level(
                "input",
                0.0,
            )

    def transcribe_file(
        self,
        audio_file: str,
    ) -> str:

        if (
            self._speech_to_text
            is None
        ):
            return ""

        try:

            transcription = (
                self._speech_to_text
                .transcribe(
                    audio_file
                )
            )

            return (
                transcription.strip()
            )

        except Exception as error:

            self._logger.error(
                "Errore trascrizione audio: "
                f"{error}"
            )

            return ""

    def speak(
        self,
        text: str,
    ) -> None:

        if not self.initialized:

            raise RuntimeError(
                "Audio Engine non inizializzato."
            )

        if self._voice_manager is None:

            raise RuntimeError(
                "Voice Manager non disponibile."
            )

        clean_text = (
            text.strip()
        )

        if not clean_text:
            return

        try:

            self._voice_manager.speak(
                clean_text
            )

        except Exception as error:

            self._logger.error(
                "Errore durante la sintesi vocale: "
                f"{error}"
            )

        finally:

            self._emit_audio_level(
                "output",
                0.0,
            )

    def stop_speaking(
        self,
    ) -> None:

        if self._voice_manager is None:
            return

        try:

            self._voice_manager.stop()

            self._emit_audio_level(
                "output",
                0.0,
            )

        except Exception as error:

            self._logger.error(
                "Errore durante l'interruzione "
                f"della voce: {error}"
            )

    def _handle_input_level(
        self,
        level: float,
    ) -> None:

        self._emit_audio_level(
            "input",
            level,
        )

    def _handle_output_level(
        self,
        level: float,
    ) -> None:

        self._emit_audio_level(
            "output",
            level,
        )

    def _emit_audio_level(
        self,
        source: str,
        level: float,
    ) -> None:

        if (
            self._audio_level_callback
            is None
        ):
            return

        try:

            self._audio_level_callback(
                source,
                max(
                    0.0,
                    min(
                        float(level),
                        1.0,
                    ),
                ),
            )

        except Exception:
            pass