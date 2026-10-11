import time

import numpy as np
import openwakeword
import sounddevice as sd

from openwakeword.model import Model

from .wake_word_config import WakeWordConfig


class WakeWordDetector:
    """
    Rileva la Wake Word "Hey Jarvis"
    utilizzando openWakeWord.
    """

    def __init__(
        self,
        config: WakeWordConfig | None = None,
    ) -> None:
        self._config = (
            config
            or WakeWordConfig()
        )

        model_info = openwakeword.MODELS.get(
            self._config.model_name
        )

        if model_info is None:
            raise RuntimeError(
                "Modello Wake Word non trovato: "
                f"{self._config.model_name}"
            )

        model_path = model_info["model_path"]

        self._model = Model(
            wakeword_models=[
                model_path
            ],
        )

        self._threshold = (
            self._config.threshold
        )

        self._last_detection_time = 0.0
        self._last_score = 0.0

    @property
    def config(
        self,
    ) -> WakeWordConfig:
        return self._config

    @property
    def threshold(
        self,
    ) -> float:
        return self._threshold

    @property
    def last_score(
        self,
    ) -> float:
        return self._last_score

    def set_threshold(
        self,
        threshold: float,
    ) -> None:
        """
        Modifica la sensibilità della Wake Word.

        Un valore più basso rende il riconoscimento
        più sensibile.

        Un valore più alto lo rende più selettivo.
        """

        if not 0.0 < threshold <= 1.0:
            raise ValueError(
                "La sensibilità deve essere "
                "compresa tra 0 e 1."
            )

        self._threshold = threshold

        self._model.reset()

    def listen_once(self) -> bool:
        """
        Rimane in ascolto fino al rilevamento
        della Wake Word.
        """

        self._model.reset()
        self._last_score = 0.0

        try:
            with sd.InputStream(
                samplerate=self._config.sample_rate,
                channels=1,
                dtype="int16",
                blocksize=self._config.chunk_size,
            ) as stream:

                while True:
                    try:
                        audio, overflowed = stream.read(
                            self._config.chunk_size
                        )

                    except sd.PortAudioError as error:
                        print(
                            "Errore durante la lettura "
                            f"del microfono: {error}"
                        )

                        return False

                    if overflowed:
                        continue

                    audio_data = np.asarray(
                        audio,
                        dtype=np.int16,
                    ).reshape(-1)

                    prediction = self._model.predict(
                        audio_data
                    )

                    score = self._get_score(
                        prediction
                    )

                    self._last_score = score

                    if score < self._threshold:
                        continue

                    current_time = time.monotonic()

                    elapsed = (
                        current_time
                        - self._last_detection_time
                    )

                    if (
                        elapsed
                        < self._config.cooldown_seconds
                    ):
                        continue

                    self._last_detection_time = (
                        current_time
                    )

                    self._model.reset()

                    return True

        except sd.PortAudioError as error:
            print(
                "Impossibile avviare il microfono "
                f"per la Wake Word: {error}"
            )

            return False

    def reset(self) -> None:
        """
        Reimposta lo stato interno del detector.
        """

        self._model.reset()

        self._last_detection_time = 0.0
        self._last_score = 0.0

    def _get_score(
        self,
        prediction: dict,
    ) -> float:
        if not prediction:
            return 0.0

        if self._config.model_name in prediction:
            return float(
                prediction[
                    self._config.model_name
                ]
            )

        for key, value in prediction.items():
            if "jarvis" in str(key).lower():
                return float(value)

        return 0.0