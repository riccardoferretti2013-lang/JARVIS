from collections.abc import Callable
from pathlib import Path
from tempfile import NamedTemporaryFile

import sys
import threading
import time
import wave
import winsound

import numpy as np
from piper import PiperVoice

from ...config.settings_manager import SettingsManager
from ...services.logger_service import LoggerService
from ..processing import VoicePipeline
from .base_tts import BaseTTS


AudioLevelCallback = Callable[
    [float],
    None,
]


class PiperTTS(BaseTTS):

    DEFAULT_MODEL_PATH = Path(
        "assets/voices/it_IT-riccardo-x_low.onnx"
    )

    def __init__(
        self,
        settings: SettingsManager,
        logger: LoggerService,
        audio_level_callback: AudioLevelCallback | None = None,
    ) -> None:

        self._settings = settings
        self._logger = logger
        self._pipeline = VoicePipeline()

        self._audio_level_callback = (
            audio_level_callback
        )

        self._voice: PiperVoice | None = None

        self._is_speaking = False

        self._playback_finished = (
            threading.Event()
        )

        self._level_stop = (
            threading.Event()
        )

        self._level_thread: (
            threading.Thread | None
        ) = None

        configured_path = Path(
            str(
                self._settings.get(
                    "piper_model_path",
                    str(self.DEFAULT_MODEL_PATH),
                )
            )
        )

        self._model_path = (
            self._resolve_resource_path(
                configured_path
            )
        )

        self._initialize_voice()

    @property
    def engine_name(
        self,
    ) -> str:
        return "Piper"

    @property
    def is_speaking(
        self,
    ) -> bool:
        return self._is_speaking

    def set_audio_level_callback(
        self,
        callback: AudioLevelCallback | None,
    ) -> None:

        self._audio_level_callback = (
            callback
        )

    def is_available(
        self,
    ) -> bool:

        return (
            self._voice is not None
            and self._model_path.exists()
        )

    def speak(
        self,
        text: str,
    ) -> None:

        if not text:
            return

        if not self.is_available():
            raise RuntimeError(
                "Il motore Piper non è disponibile."
            )

        processed_text = (
            self._pipeline.process(
                text
            )
        )

        if not processed_text:
            return

        temporary_path: Path | None = None

        try:

            with NamedTemporaryFile(
                suffix=".wav",
                delete=False,
            ) as temporary_file:

                temporary_path = Path(
                    temporary_file.name
                )

            with wave.open(
                str(temporary_path),
                "wb",
            ) as wav_file:

                self._voice.synthesize_wav(
                    processed_text,
                    wav_file,
                )

            duration = (
                self._get_wav_duration(
                    temporary_path
                )
            )

            self._playback_finished.clear()
            self._level_stop.clear()

            self._is_speaking = True

            winsound.PlaySound(
                str(temporary_path),
                winsound.SND_FILENAME
                | winsound.SND_ASYNC,
            )

            self._start_level_monitor(
                temporary_path
            )

            self._playback_finished.wait(
                timeout=duration + 1.0
            )

        except Exception as error:

            self._logger.error(
                "Errore durante la sintesi Piper: "
                f"{error}"
            )

            raise RuntimeError(
                "Errore durante la sintesi vocale Piper."
            ) from error

        finally:

            self.stop()

            if (
                temporary_path is not None
                and temporary_path.exists()
            ):

                try:
                    temporary_path.unlink()

                except OSError:

                    self._logger.warning(
                        "Impossibile eliminare il file "
                        "audio temporaneo di Piper."
                    )

    def stop(
        self,
    ) -> None:

        self._level_stop.set()

        if self._is_speaking:

            try:
                winsound.PlaySound(
                    None,
                    winsound.SND_PURGE,
                )

            except RuntimeError:
                pass

        self._is_speaking = False

        self._playback_finished.set()

        level_thread = (
            self._level_thread
        )

        if (
            level_thread is not None
            and level_thread.is_alive()
            and level_thread
            is not threading.current_thread()
        ):

            level_thread.join(
                timeout=0.25
            )

        self._level_thread = None

        self._emit_level(
            0.0
        )

    def _start_level_monitor(
        self,
        path: Path,
    ) -> None:

        self._level_thread = (
            threading.Thread(
                target=self._monitor_wav_level,
                args=(path,),
                daemon=True,
                name="JarvisPiperLevel",
            )
        )

        self._level_thread.start()

    def _monitor_wav_level(
        self,
        path: Path,
    ) -> None:

        try:

            with wave.open(
                str(path),
                "rb",
            ) as wav_file:

                frame_rate = (
                    wav_file.getframerate()
                )

                sample_width = (
                    wav_file.getsampwidth()
                )

                if frame_rate <= 0:
                    return

                chunk_seconds = 0.045

                frames_per_chunk = max(
                    1,
                    int(
                        frame_rate
                        * chunk_seconds
                    ),
                )

                smoothed = 0.0

                while (
                    not self._level_stop.is_set()
                ):

                    started = (
                        time.perf_counter()
                    )

                    frames = (
                        wav_file.readframes(
                            frames_per_chunk
                        )
                    )

                    if not frames:
                        break

                    rms = (
                        self._calculate_rms(
                            frames,
                            sample_width,
                        )
                    )

                    normalized = min(
                        rms / 6500.0,
                        1.0,
                    )

                    if normalized > smoothed:

                        smoothed = (
                            smoothed * 0.20
                            + normalized * 0.80
                        )

                    else:

                        smoothed = (
                            smoothed * 0.68
                            + normalized * 0.32
                        )

                    self._emit_level(
                        smoothed
                    )

                    elapsed = (
                        time.perf_counter()
                        - started
                    )

                    remaining = max(
                        0.0,
                        chunk_seconds
                        - elapsed,
                    )

                    if remaining > 0:

                        self._level_stop.wait(
                            remaining
                        )

        except Exception as error:

            self._logger.warning(
                "Impossibile analizzare "
                "il livello audio Piper: "
                f"{error}"
            )

        finally:

            self._emit_level(
                0.0
            )

    @staticmethod
    def _calculate_rms(
        frames: bytes,
        sample_width: int,
    ) -> float:

        if not frames:
            return 0.0

        if sample_width == 1:

            samples = np.frombuffer(
                frames,
                dtype=np.uint8,
            ).astype(
                np.float64
            )

            samples -= 128.0

        elif sample_width == 2:

            samples = np.frombuffer(
                frames,
                dtype="<i2",
            ).astype(
                np.float64
            )

        elif sample_width == 4:

            samples = np.frombuffer(
                frames,
                dtype="<i4",
            ).astype(
                np.float64
            )

        else:
            return 0.0

        if samples.size == 0:
            return 0.0

        return float(
            np.sqrt(
                np.mean(
                    np.square(
                        samples
                    )
                )
            )
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

        level = max(
            0.0,
            min(
                float(level),
                1.0,
            ),
        )

        try:

            self._audio_level_callback(
                level
            )

        except Exception:
            pass

    @staticmethod
    def _get_wav_duration(
        path: Path,
    ) -> float:

        with wave.open(
            str(path),
            "rb",
        ) as wav_file:

            frames = (
                wav_file.getnframes()
            )

            frame_rate = (
                wav_file.getframerate()
            )

        if frame_rate <= 0:
            return 0.0

        return frames / float(
            frame_rate
        )

    @staticmethod
    def _runtime_root() -> Path:

        if getattr(
            sys,
            "frozen",
            False,
        ):

            return Path(
                sys._MEIPASS
            )

        return (
            Path(__file__)
            .resolve()
            .parents[4]
        )

    @classmethod
    def _resolve_resource_path(
        cls,
        path: Path,
    ) -> Path:

        if path.is_absolute():
            return path

        return (
            cls._runtime_root()
            / path
        ).resolve()

    def _initialize_voice(
        self,
    ) -> None:

        if not self._model_path.exists():

            self._logger.error(
                "Modello Piper non trovato: "
                f"{self._model_path}"
            )

            return

        try:

            self._logger.info(
                "Caricamento della voce Piper..."
            )

            self._voice = (
                PiperVoice.load(
                    str(
                        self._model_path
                    )
                )
            )

            self._logger.info(
                "Piper inizializzato correttamente "
                f"con il modello: "
                f"{self._model_path.name}"
            )

        except Exception as error:

            self._voice = None

            self._logger.error(
                "Impossibile inizializzare Piper: "
                f"{error}"
            )