import tempfile
import time
from collections.abc import Callable

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

from ...config.configuration import Configuration


AudioLevelCallback = Callable[[float], None]


class Microphone:
    """
    Gestisce la registrazione audio dal microfono.

    Può inoltre inviare in tempo reale il livello
    audio normalizzato da 0.0 a 1.0.
    """

    def __init__(
        self,
        audio_level_callback: AudioLevelCallback | None = None,
    ) -> None:

        self.sample_rate = (
            Configuration.AUDIO_SAMPLE_RATE
        )

        self.duration = (
            Configuration.AUDIO_RECORDING_DURATION
        )

        self.channels = (
            Configuration.AUDIO_CHANNELS
        )

        self.dtype = (
            Configuration.AUDIO_DTYPE
        )

        self._audio_level_callback = (
            audio_level_callback
        )

        self._smoothed_level = 0.0

    def set_audio_level_callback(
        self,
        callback: AudioLevelCallback | None,
    ) -> None:

        self._audio_level_callback = callback

    def record(
        self,
        timeout_seconds: float | None = None,
    ) -> str:

        if (
            timeout_seconds is not None
            and timeout_seconds <= 0
        ):
            raise ValueError(
                "timeout_seconds deve essere maggiore di zero."
            )

        print(
            "🎤 Sto ascoltando..."
        )

        try:

            if timeout_seconds is None:
                return self._record_fixed_duration()

            return self._record_with_timeout(
                timeout_seconds
            )

        finally:
            self._emit_level(
                0.0,
                immediate=True,
            )

    def _record_fixed_duration(
        self,
    ) -> str:

        chunk_duration = 0.05

        chunk_size = max(
            1,
            int(
                self.sample_rate
                * chunk_duration
            ),
        )

        total_samples = int(
            self.duration
            * self.sample_rate
        )

        remaining_samples = (
            total_samples
        )

        recorded_chunks: list[
            np.ndarray
        ] = []

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=self.dtype,
            blocksize=chunk_size,
        ) as stream:

            while remaining_samples > 0:

                read_size = min(
                    chunk_size,
                    remaining_samples,
                )

                audio_chunk, overflowed = (
                    stream.read(
                        read_size
                    )
                )

                if overflowed:
                    continue

                copied_chunk = (
                    audio_chunk.copy()
                )

                recorded_chunks.append(
                    copied_chunk
                )

                self._process_audio_level(
                    copied_chunk
                )

                remaining_samples -= (
                    read_size
                )

        if not recorded_chunks:
            return ""

        recording = np.concatenate(
            recorded_chunks,
            axis=0,
        )

        return self._save_recording(
            recording
        )

    def _record_with_timeout(
        self,
        timeout_seconds: float,
    ) -> str:

        chunk_duration = 0.05

        chunk_size = max(
            1,
            int(
                self.sample_rate
                * chunk_duration
            ),
        )

        silence_threshold = 500

        start_time = (
            time.monotonic()
        )

        recorded_chunks: list[
            np.ndarray
        ] = []

        speech_detected = False

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=self.dtype,
            blocksize=chunk_size,
        ) as stream:

            while True:

                audio_chunk, overflowed = (
                    stream.read(
                        chunk_size
                    )
                )

                if overflowed:
                    continue

                copied_chunk = (
                    audio_chunk.copy()
                )

                recorded_chunks.append(
                    copied_chunk
                )

                self._process_audio_level(
                    copied_chunk
                )

                amplitude = self._peak_amplitude(
                    copied_chunk
                )

                if (
                    amplitude
                    >= silence_threshold
                ):
                    speech_detected = True
                    break

                elapsed = (
                    time.monotonic()
                    - start_time
                )

                if (
                    elapsed
                    >= timeout_seconds
                ):
                    return ""

            remaining_duration = max(
                0.0,
                self.duration
                - (
                    time.monotonic()
                    - start_time
                ),
            )

            remaining_samples = int(
                remaining_duration
                * self.sample_rate
            )

            while (
                speech_detected
                and remaining_samples > 0
            ):

                read_size = min(
                    chunk_size,
                    remaining_samples,
                )

                audio_chunk, overflowed = (
                    stream.read(
                        read_size
                    )
                )

                if overflowed:
                    continue

                copied_chunk = (
                    audio_chunk.copy()
                )

                recorded_chunks.append(
                    copied_chunk
                )

                self._process_audio_level(
                    copied_chunk
                )

                remaining_samples -= (
                    read_size
                )

        if not recorded_chunks:
            return ""

        recording = np.concatenate(
            recorded_chunks,
            axis=0,
        )

        return self._save_recording(
            recording
        )

    def _process_audio_level(
        self,
        audio_chunk: np.ndarray,
    ) -> None:

        if audio_chunk.size == 0:
            return

        samples = audio_chunk.astype(
            np.float64
        )

        rms = float(
            np.sqrt(
                np.mean(
                    np.square(
                        samples
                    )
                )
            )
        )

        if np.issubdtype(
            audio_chunk.dtype,
            np.floating,
        ):
            raw_level = min(
                rms * 3.5,
                1.0,
            )

        else:
            raw_level = min(
                rms / 6000.0,
                1.0,
            )

        if raw_level < 0.008:
            raw_level = 0.0

        self._emit_level(
            raw_level
        )

    def _emit_level(
        self,
        level: float,
        immediate: bool = False,
    ) -> None:

        level = max(
            0.0,
            min(
                float(level),
                1.0,
            ),
        )

        if immediate:
            self._smoothed_level = level

        elif level > self._smoothed_level:

            self._smoothed_level = (
                self._smoothed_level
                * 0.25
                + level
                * 0.75
            )

        else:

            self._smoothed_level = (
                self._smoothed_level
                * 0.72
                + level
                * 0.28
            )

        if self._audio_level_callback is None:
            return

        try:
            self._audio_level_callback(
                self._smoothed_level
            )

        except Exception:
            pass

    @staticmethod
    def _peak_amplitude(
        audio_chunk: np.ndarray,
    ) -> float:

        if audio_chunk.size == 0:
            return 0.0

        return float(
            np.max(
                np.abs(
                    audio_chunk.astype(
                        np.float64
                    )
                )
            )
        )

    def _save_recording(
        self,
        recording: np.ndarray,
    ) -> str:

        temp_file = (
            tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".wav",
            )
        )

        temp_file.close()

        write(
            temp_file.name,
            self.sample_rate,
            recording,
        )

        return temp_file.name