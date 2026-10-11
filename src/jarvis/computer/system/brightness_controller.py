import screen_brightness_control as sbc


class BrightnessController:
    """
    Gestisce la luminosità dello schermo su Windows.
    """

    DEFAULT_STEP = 10

    def __init__(
        self,
        step: int = DEFAULT_STEP,
    ) -> None:
        if not 1 <= step <= 100:
            raise ValueError(
                "Lo step della luminosità deve essere "
                "compreso tra 1 e 100."
            )

        self._step = step

    @property
    def step(self) -> int:
        return self._step

    def get_brightness(self) -> int:
        """
        Restituisce la luminosità corrente.
        """

        values = sbc.get_brightness()

        if not values:
            raise RuntimeError(
                "Impossibile leggere la luminosità."
            )

        return int(values[0])

    def set_brightness(
        self,
        value: int,
    ) -> int:
        """
        Imposta la luminosità tra 0 e 100.
        """

        normalized_value = max(
            0,
            min(
                100,
                int(value),
            ),
        )

        sbc.set_brightness(
            normalized_value
        )

        return self.get_brightness()

    def increase(
        self,
        amount: int | None = None,
    ) -> int:
        """
        Aumenta la luminosità.
        """

        step = (
            self._step
            if amount is None
            else int(amount)
        )

        return self.set_brightness(
            self.get_brightness() + step
        )

    def decrease(
        self,
        amount: int | None = None,
    ) -> int:
        """
        Diminuisce la luminosità.
        """

        step = (
            self._step
            if amount is None
            else int(amount)
        )

        return self.set_brightness(
            self.get_brightness() - step
        )