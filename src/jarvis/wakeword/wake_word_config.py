from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WakeWordConfig:
    """
    Configurazione del sistema Wake Word.
    """

    model_name: str = "hey_jarvis"

    threshold: float = 0.5

    sample_rate: int = 16000

    chunk_size: int = 1280

    cooldown_seconds: float = 1.5

    def __post_init__(self) -> None:
        if not 0.0 < self.threshold <= 1.0:
            raise ValueError(
                "threshold deve essere compreso tra 0 e 1."
            )

        if self.sample_rate < 8000:
            raise ValueError(
                "sample_rate non valido."
            )

        if self.chunk_size < 1:
            raise ValueError(
                "chunk_size deve essere almeno 1."
            )

        if self.cooldown_seconds < 0:
            raise ValueError(
                "cooldown_seconds non può essere negativo."
            )