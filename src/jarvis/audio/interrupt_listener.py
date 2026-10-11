from collections.abc import Callable

import keyboard

from ..services.logger_service import LoggerService


class InterruptListener:
    """
    Gestisce lo stop immediato
    della risposta di J.A.R.V.I.S.

    ESC:
    - interrompe la voce
    - interrompe lo streaming AI
    - svuota la coda vocale
    """

    def __init__(
        self,
        logger: LoggerService,
        cancel_callback: Callable[[], bool],
    ) -> None:
        self._logger = logger

        self._cancel_callback = (
            cancel_callback
        )

        self._started = False

        self._hotkey = None

    def start(
        self,
    ) -> None:
        if self._started:
            return

        self._hotkey = keyboard.add_hotkey(
            "esc",
            self._handle_escape,
            suppress=False,
        )

        self._started = True

        self._logger.info(
            "Interrupt Listener avviato."
        )

    def stop(
        self,
    ) -> None:
        if not self._started:
            return

        try:
            if self._hotkey is not None:
                keyboard.remove_hotkey(
                    self._hotkey
                )

        except Exception:
            pass

        self._hotkey = None
        self._started = False

    def _handle_escape(
        self,
    ) -> None:

        try:
            interrupted = (
                self._cancel_callback()
            )

            if not interrupted:
                return

            self._logger.info(
                "ESC rilevato: "
                "risposta interrotta."
            )

            print(
                "\n[J.A.R.V.I.S. interrotto]"
            )

        except Exception as error:
            self._logger.error(
                "Errore interruzione risposta: "
                f"{error}"
            )