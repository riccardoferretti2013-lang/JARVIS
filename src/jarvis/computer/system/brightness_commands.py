import re

from .brightness_controller import BrightnessController


class BrightnessCommands:
    """
    Gestisce i comandi relativi
    alla luminosità dello schermo.
    """

    def __init__(
        self,
        controller: BrightnessController | None = None,
    ) -> None:
        self._controller = (
            controller
            or BrightnessController()
        )

    def process(
        self,
        command: str,
    ) -> str | None:
        clean_command = (
            command
            .strip()
            .lower()
        )

        if not clean_command:
            return None

        if clean_command in {
            "luminosità",
            "luminosita",
            "luminosità attuale",
            "luminosita attuale",
        }:
            return self._get_brightness()

        if clean_command in {
            "alza luminosità",
            "alza luminosita",
            "aumenta luminosità",
            "aumenta luminosita",
            "aumenta la luminosità",
            "aumenta la luminosita",
        }:
            return self._increase_brightness()

        if clean_command in {
            "abbassa luminosità",
            "abbassa luminosita",
            "diminuisci luminosità",
            "diminuisci luminosita",
            "diminuisci la luminosità",
            "diminuisci la luminosita",
        }:
            return self._decrease_brightness()

        value = self._extract_brightness(
            clean_command
        )

        if value is not None:
            return self._set_brightness(
                value
            )

        return None

    def _get_brightness(
        self,
    ) -> str:
        value = (
            self._controller.get_brightness()
        )

        return (
            f"La luminosità è al {value}%."
        )

    def _set_brightness(
        self,
        value: int,
    ) -> str:
        new_value = (
            self._controller.set_brightness(
                value
            )
        )

        return (
            f"Luminosità impostata al {new_value}%."
        )

    def _increase_brightness(
        self,
    ) -> str:
        value = (
            self._controller.increase()
        )

        return (
            f"Luminosità aumentata al {value}%."
        )

    def _decrease_brightness(
        self,
    ) -> str:
        value = (
            self._controller.decrease()
        )

        return (
            f"Luminosità abbassata al {value}%."
        )

    @staticmethod
    def _extract_brightness(
        command: str,
    ) -> int | None:
        patterns = [
            r"^luminosità\s+(\d{1,3})$",
            r"^luminosita\s+(\d{1,3})$",
            r"^luminosità\s+al\s+(\d{1,3})$",
            r"^luminosita\s+al\s+(\d{1,3})$",
            r"^imposta\s+luminosità\s+al\s+(\d{1,3})$",
            r"^imposta\s+luminosita\s+al\s+(\d{1,3})$",
            r"^imposta\s+la\s+luminosità\s+al\s+(\d{1,3})$",
            r"^imposta\s+la\s+luminosita\s+al\s+(\d{1,3})$",
        ]

        for pattern in patterns:
            match = re.fullmatch(
                pattern,
                command,
            )

            if match is None:
                continue

            value = int(
                match.group(1)
            )

            return max(
                0,
                min(
                    100,
                    value,
                ),
            )

        return None