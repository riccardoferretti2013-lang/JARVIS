from pycaw.pycaw import AudioUtilities


class VolumeController:
    """
    Gestisce il volume principale di Windows.
    """

    DEFAULT_STEP = 5

    def __init__(
        self,
        step: int = DEFAULT_STEP,
    ) -> None:
        if not 1 <= step <= 100:
            raise ValueError(
                "Lo step del volume deve essere "
                "compreso tra 1 e 100."
            )

        self._step = step

    @property
    def step(self) -> int:
        return self._step

    def get_volume(self) -> int:
        """
        Restituisce il volume corrente da 0 a 100.
        """

        endpoint = self._get_endpoint()

        level = (
            endpoint.GetMasterVolumeLevelScalar()
        )

        return round(
            float(level) * 100
        )

    def set_volume(
        self,
        value: int,
    ) -> int:
        """
        Imposta il volume tra 0 e 100.
        """

        normalized_value = max(
            0,
            min(
                100,
                int(value),
            ),
        )

        endpoint = self._get_endpoint()

        endpoint.SetMasterVolumeLevelScalar(
            normalized_value / 100,
            None,
        )

        return self.get_volume()

    def increase(
        self,
        amount: int | None = None,
    ) -> int:
        """
        Aumenta il volume.
        """

        step = (
            self._step
            if amount is None
            else int(amount)
        )

        return self.set_volume(
            self.get_volume() + step
        )

    def decrease(
        self,
        amount: int | None = None,
    ) -> int:
        """
        Abbassa il volume.
        """

        step = (
            self._step
            if amount is None
            else int(amount)
        )

        return self.set_volume(
            self.get_volume() - step
        )

    def mute(self) -> bool:
        """
        Disattiva l'audio.
        """

        endpoint = self._get_endpoint()

        endpoint.SetMute(
            1,
            None,
        )

        return self.is_muted()

    def unmute(self) -> bool:
        """
        Riattiva l'audio.
        """

        endpoint = self._get_endpoint()

        endpoint.SetMute(
            0,
            None,
        )

        return not self.is_muted()

    def toggle_mute(self) -> bool:
        """
        Inverte lo stato mute.

        Restituisce True se dopo
        l'operazione l'audio è muto.
        """

        if self.is_muted():
            self.unmute()
            return False

        self.mute()

        return True

    def is_muted(self) -> bool:
        """
        Restituisce True se Windows è in mute.
        """

        endpoint = self._get_endpoint()

        return bool(
            endpoint.GetMute()
        )

    @staticmethod
    def _get_endpoint():
        """
        Recupera l'interfaccia del volume
        principale di Windows.
        """

        device = (
            AudioUtilities.GetSpeakers()
        )

        endpoint = device.EndpointVolume

        if endpoint is None:
            raise RuntimeError(
                "Impossibile accedere al controllo "
                "del volume di Windows."
            )

        return endpoint