import numpy as np
import sounddevice as sd

from .feedback_sound import FeedbackSound


class FeedbackPlayer:
    """
    Riproduce brevi segnali sonori di sistema.
    """

    SAMPLE_RATE = 44100

    def play(
        self,
        sound: FeedbackSound,
    ) -> None:
        """
        Riproduce il feedback in modo sincrono.
        """

        waveform = self._build_waveform(
            sound
        )

        try:
            sd.play(
                waveform,
                samplerate=self.SAMPLE_RATE,
                blocking=True,
            )

        except Exception:
            return

    def _build_waveform(
        self,
        sound: FeedbackSound,
    ) -> np.ndarray:
        if sound == FeedbackSound.WAKE:
            return self._double_tone(
                first_frequency=700,
                second_frequency=1000,
            )

        if sound == FeedbackSound.LISTENING:
            return self._tone(
                frequency=900,
                duration=0.12,
            )

        if sound == FeedbackSound.SUCCESS:
            return self._double_tone(
                first_frequency=900,
                second_frequency=1200,
            )

        if sound == FeedbackSound.TIMEOUT:
            return self._double_tone(
                first_frequency=700,
                second_frequency=450,
            )

        if sound == FeedbackSound.ERROR:
            return self._double_tone(
                first_frequency=350,
                second_frequency=250,
            )

        if sound == FeedbackSound.STANDBY:
            return self._tone(
                frequency=450,
                duration=0.15,
            )

        return self._tone(
            frequency=600,
            duration=0.1,
        )

    def _tone(
        self,
        frequency: float,
        duration: float,
        volume: float = 0.25,
    ) -> np.ndarray:
        sample_count = int(
            self.SAMPLE_RATE
            * duration
        )

        time_axis = (
            np.arange(sample_count)
            / self.SAMPLE_RATE
        )

        waveform = (
            volume
            * np.sin(
                2
                * np.pi
                * frequency
                * time_axis
            )
        )

        fade_samples = min(
            int(
                self.SAMPLE_RATE
                * 0.02
            ),
            sample_count // 2,
        )

        if fade_samples > 0:
            fade_in = np.linspace(
                0.0,
                1.0,
                fade_samples,
            )

            fade_out = np.linspace(
                1.0,
                0.0,
                fade_samples,
            )

            waveform[:fade_samples] *= fade_in
            waveform[-fade_samples:] *= fade_out

        return waveform.astype(
            np.float32
        )

    def _double_tone(
        self,
        first_frequency: float,
        second_frequency: float,
    ) -> np.ndarray:
        first = self._tone(
            frequency=first_frequency,
            duration=0.09,
        )

        pause = np.zeros(
            int(
                self.SAMPLE_RATE
                * 0.04
            ),
            dtype=np.float32,
        )

        second = self._tone(
            frequency=second_frequency,
            duration=0.11,
        )

        return np.concatenate(
            [
                first,
                pause,
                second,
            ]
        )