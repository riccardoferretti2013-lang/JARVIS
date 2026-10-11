from collections.abc import Callable

from ...config.settings_manager import SettingsManager
from ...services.logger_service import LoggerService
from .base_tts import BaseTTS
from .piper_tts import PiperTTS
from .pyttsx3_tts import Pyttsx3TTS


AudioLevelCallback = Callable[
    [float],
    None,
]


class VoiceManager:

    def __init__(
        self,
        settings: SettingsManager,
        logger: LoggerService,
        audio_level_callback: AudioLevelCallback | None = None,
    ) -> None:

        self._settings = settings
        self._logger = logger

        self._audio_level_callback = (
            audio_level_callback
        )

        self._engine: BaseTTS = (
            self._create_engine()
        )

        self._logger.info(
            "Motore vocale attivo: "
            f"{self._engine.engine_name}"
        )

    @property
    def engine(
        self,
    ) -> BaseTTS:
        return self._engine

    @property
    def engine_name(
        self,
    ) -> str:
        return self._engine.engine_name

    @property
    def is_speaking(
        self,
    ) -> bool:

        return bool(
            getattr(
                self._engine,
                "is_speaking",
                False,
            )
        )

    def set_audio_level_callback(
        self,
        callback: AudioLevelCallback | None,
    ) -> None:

        self._audio_level_callback = callback

        setter = getattr(
            self._engine,
            "set_audio_level_callback",
            None,
        )

        if callable(
            setter
        ):
            setter(
                callback
            )

    def is_available(
        self,
    ) -> bool:

        return self._engine.is_available()

    def speak(
        self,
        text: str,
    ) -> None:

        if not text:
            return

        try:

            self._engine.speak(
                text
            )

        except Exception as error:

            self._logger.error(
                "Errore del motore vocale "
                f"{self._engine.engine_name}: "
                f"{error}"
            )

            if isinstance(
                self._engine,
                Pyttsx3TTS,
            ):
                raise

            self._logger.warning(
                "Passaggio automatico a pyttsx3."
            )

            self._engine = (
                Pyttsx3TTS(
                    settings=self._settings,
                    logger=self._logger,
                )
            )

            self._engine.speak(
                text
            )

    def stop(
        self,
    ) -> None:

        self._engine.stop()

        self._emit_level(
            0.0
        )

    def _create_engine(
        self,
    ) -> BaseTTS:

        configured_engine = str(
            self._settings.get(
                "voice_engine",
                "piper",
            )
        ).strip().lower()

        if (
            configured_engine
            == "pyttsx3"
        ):

            return Pyttsx3TTS(
                settings=self._settings,
                logger=self._logger,
            )

        if configured_engine not in {
            "piper",
            "pyttsx3",
        }:

            self._logger.warning(
                "Motore vocale non riconosciuto: "
                f"{configured_engine}. Uso Piper."
            )

        piper = PiperTTS(
            settings=self._settings,
            logger=self._logger,
            audio_level_callback=(
                self._audio_level_callback
            ),
        )

        if piper.is_available():
            return piper

        self._logger.warning(
            "Piper non è disponibile. "
            "Uso pyttsx3 come fallback."
        )

        return Pyttsx3TTS(
            settings=self._settings,
            logger=self._logger,
        )

    def _emit_level(
        self,
        level: float,
    ) -> None:

        if (
            self._audio_level_callback
            is None
        ):
            return

        try:
            self._audio_level_callback(
                level
            )

        except Exception:
            pass