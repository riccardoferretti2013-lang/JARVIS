import pyttsx3

from ...config.settings_manager import SettingsManager
from ...services.logger_service import LoggerService
from ..processing import VoicePipeline
from .base_tts import BaseTTS


class Pyttsx3TTS(BaseTTS):
    """
    Motore vocale di fallback basato su pyttsx3.
    """

    def __init__(
        self,
        settings: SettingsManager,
        logger: LoggerService,
    ) -> None:
        self._settings = settings
        self._logger = logger
        self._pipeline = VoicePipeline()
        self._engine = pyttsx3.init()

        self._configure_engine()

        self._logger.info(
            "Pyttsx3 inizializzato come motore vocale di fallback."
        )

    @property
    def engine_name(self) -> str:
        return "pyttsx3"

    def is_available(self) -> bool:
        return self._engine is not None

    def speak(self, text: str) -> None:
        if not text:
            return

        processed_text = self._pipeline.process(text)

        if not processed_text:
            return

        try:
            self._engine.say(processed_text)
            self._engine.runAndWait()

        except Exception as error:
            self._logger.error(
                "Errore durante la sintesi pyttsx3: "
                f"{error}"
            )

            raise RuntimeError(
                "Errore durante la sintesi vocale pyttsx3."
            ) from error

    def stop(self) -> None:
        self._engine.stop()

    def _configure_engine(self) -> None:
        voice_rate = self._settings.get(
            "voice_rate",
            185,
        )

        voice_volume = self._settings.get(
            "voice_volume",
            1.0,
        )

        self._engine.setProperty(
            "rate",
            voice_rate,
        )

        self._engine.setProperty(
            "volume",
            voice_volume,
        )

        voices = self._engine.getProperty("voices")

        if voices:
            self._engine.setProperty(
                "voice",
                voices[0].id,
            )