import os

from faster_whisper import WhisperModel

from ...config.settings_manager import SettingsManager
from ...services.logger_service import LoggerService


class SpeechToText:
    def __init__(
        self,
        settings: SettingsManager,
        logger: LoggerService
    ):
        self._settings = settings
        self._logger = logger

        self._logger.info(
            "Caricamento del modello Whisper."
        )

        self.language = self._settings.get(
            "language",
            "it"
        )

        self.beam_size = self._settings.get(
            "whisper_beam_size",
            5
        )

        whisper_model = self._settings.get(
            "whisper_model",
            "small"
        )

        whisper_device = self._settings.get(
            "whisper_device",
            "cpu"
        )

        whisper_compute_type = self._settings.get(
            "whisper_compute_type",
            "int8"
        )

        try:
            self.model = WhisperModel(
                whisper_model,
                device=whisper_device,
                compute_type=whisper_compute_type
            )

        except Exception as error:
            self._logger.error(
                "Errore durante il caricamento di Whisper: "
                f"{error}"
            )

            raise RuntimeError(
                "Impossibile inizializzare il modello Whisper."
            ) from error

        self._logger.info(
            "Modello Whisper pronto."
        )

    def transcribe(self, audio_file: str) -> str:
        try:
            segments, _ = self.model.transcribe(
                audio_file,
                language=self.language,
                task="transcribe",
                beam_size=self.beam_size,
                vad_filter=True,
                condition_on_previous_text=False,
                initial_prompt=(
                    "Assistente vocale JARVIS. "
                    "Possibili comandi: "
                    "ciao, come stai, "
                    "che ore sono, "
                    "che data è, "
                    "esci, "
                    "chiudi Jarvis, "
                    "spegni Jarvis."
                )
            )

            text = " ".join(
                segment.text.strip()
                for segment in segments
            ).strip()

            if text:
                self._logger.info(
                    f"Trascrizione riconosciuta: {text}"
                )
            else:
                self._logger.warning(
                    "Nessuna frase rilevata."
                )

            return text

        except Exception as error:
            self._logger.error(
                "Errore durante il riconoscimento vocale: "
                f"{error}"
            )

            return ""

        finally:
            if os.path.exists(audio_file):
                try:
                    os.remove(audio_file)

                except OSError as error:
                    self._logger.warning(
                        "Impossibile eliminare il file audio "
                        f"temporaneo: {error}"
                    )