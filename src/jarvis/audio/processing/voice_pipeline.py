from .pronunciation_engine import PronunciationEngine
from .text_cleaner import SpeechTextCleaner


class VoicePipeline:
    """
    Pipeline completa di preparazione del testo
    destinato alla sintesi vocale.

    Ordine:

    AI
        ↓
    Text Cleaner
        ↓
    Pronunciation Engine
        ↓
    Voce
    """

    def __init__(self) -> None:
        self._cleaner = SpeechTextCleaner()
        self._pronunciation = PronunciationEngine()

    @property
    def cleaner(self) -> SpeechTextCleaner:
        return self._cleaner

    @property
    def pronunciation(self) -> PronunciationEngine:
        return self._pronunciation

    def process(
        self,
        text: str,
    ) -> str:
        """
        Restituisce il testo ottimizzato
        per essere pronunciato.
        """

        cleaned = self._cleaner.clean(text)

        pronounced = self._pronunciation.process(
            cleaned
        )

        return pronounced