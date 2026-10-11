from ..config.settings_manager import SettingsManager

from .wake_word_detector import WakeWordDetector


class WakeWordManager:
    """
    Gestisce stato e sensibilità
    del sistema Wake Word.
    """

    SETTINGS_KEY = "wake_word_sensitivity"

    def __init__(
        self,
        detector: WakeWordDetector | None = None,
        settings: SettingsManager | None = None,
    ) -> None:
        self._detector = (
            detector
            or WakeWordDetector()
        )

        self._settings = (
            settings
            or SettingsManager()
        )

        self._enabled = True

        self._load_saved_sensitivity()

    @property
    def detector(
        self,
    ) -> WakeWordDetector:
        return self._detector

    @property
    def settings(
        self,
    ) -> SettingsManager:
        return self._settings

    @property
    def enabled(
        self,
    ) -> bool:
        return self._enabled

    @property
    def last_score(
        self,
    ) -> float:
        return self._detector.last_score

    @property
    def sensitivity(
        self,
    ) -> float:
        return self._detector.threshold

    def enable(
        self,
    ) -> None:
        self._enabled = True
        self._detector.reset()

    def disable(
        self,
    ) -> None:
        self._enabled = False
        self._detector.reset()

    def toggle(
        self,
    ) -> bool:
        self._enabled = not self._enabled

        self._detector.reset()

        return self._enabled

    def set_sensitivity(
        self,
        value: float,
    ) -> float:
        """
        Imposta e salva permanentemente
        la sensibilità della Wake Word.
        """

        self._detector.set_threshold(
            value
        )

        self._settings.set(
            self.SETTINGS_KEY,
            self._detector.threshold,
        )

        return self._detector.threshold

    def wait_for_wake_word(
        self,
    ) -> bool:
        if not self._enabled:
            return False

        return self._detector.listen_once()

    def reset(
        self,
    ) -> None:
        self._detector.reset()

    def _load_saved_sensitivity(
        self,
    ) -> None:
        try:
            self._settings.load()

        except FileNotFoundError:
            return

        value = self._settings.get(
            self.SETTINGS_KEY,
            None,
        )

        if value is None:
            return

        try:
            sensitivity = float(value)

            self._detector.set_threshold(
                sensitivity
            )

        except (
            TypeError,
            ValueError,
        ):
            return