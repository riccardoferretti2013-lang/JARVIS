import re

from .volume_controller import VolumeController


class VolumeCommands:
    """
    Gestisce i comandi relativi
    al volume di Windows.
    """

    def __init__(
        self,
        controller: VolumeController | None = None,
    ) -> None:
        self._controller = (
            controller
            or VolumeController()
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
            "volume",
            "volume attuale",
            "qual è il volume",
            "qual e il volume",
            "qual è il volume attuale",
            "qual e il volume attuale",
        }:
            return self._get_volume()

        if clean_command in {
            "alza volume",
            "alza il volume",
            "aumenta volume",
            "aumenta il volume",
        }:
            return self._increase_volume()

        if clean_command in {
            "abbassa volume",
            "abbassa il volume",
            "diminuisci volume",
            "diminuisci il volume",
        }:
            return self._decrease_volume()

        if clean_command in {
            "muto",
            "metti muto",
            "metti il muto",
            "disattiva audio",
            "disattiva l'audio",
        }:
            return self._mute()

        if clean_command in {
            "togli muto",
            "togli il muto",
            "riattiva audio",
            "riattiva l'audio",
        }:
            return self._unmute()

        volume_value = self._extract_volume(
            clean_command
        )

        if volume_value is not None:
            return self._set_volume(
                volume_value
            )

        return None

    def _get_volume(
        self,
    ) -> str:
        volume = (
            self._controller.get_volume()
        )

        return (
            f"Il volume è al {volume}%."
        )

    def _set_volume(
        self,
        value: int,
    ) -> str:
        volume = (
            self._controller.set_volume(
                value
            )
        )

        return (
            f"Volume impostato al {volume}%."
        )

    def _increase_volume(
        self,
    ) -> str:
        volume = (
            self._controller.increase()
        )

        return (
            f"Volume aumentato al {volume}%."
        )

    def _decrease_volume(
        self,
    ) -> str:
        volume = (
            self._controller.decrease()
        )

        return (
            f"Volume abbassato al {volume}%."
        )

    def _mute(
        self,
    ) -> str:
        self._controller.mute()

        return "Audio disattivato."

    def _unmute(
        self,
    ) -> str:
        self._controller.unmute()

        return "Audio riattivato."

    @staticmethod
    def _extract_volume(
        command: str,
    ) -> int | None:
        patterns = [
            #r"^volume\s+(\d{1,3})$",
            #r"^volume\s+al\s+(\d{1,3})$",
            r"^volume\s+(?:\w+\s+)?(\d{1,3})$",
            #r"^imposta\s+volume\s+(\d{1,3})$",
            #r"^imposta\s+volume\s+al\s+(\d{1,3})$",
            r"^imposta\s+(?:\w+\s+)?volume\s+(?:\w+\s+)?(\d{1,3})$", 
            #r"^metti\s+volume\s+al\s+(\d{1,3})$",
            #r"^metti\s+il\s+volume\s+al\s+(\d{1,3})$",
            r"^metti\s+(?:\w+\s+)?volume\s+(?:\w+\s+)?(\d{1,3})$",
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