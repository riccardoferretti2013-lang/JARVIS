import threading

from ..audio.feedback import (
    FeedbackPlayer,
    FeedbackSound,
)
from ..core.assistant import Assistant
from ..wakeword import (
    WakeWordManager,
    WakeWordSession,
)


class BackgroundWakeListener:
    """
    Gestisce la Wake Word mentre
    J.A.R.V.I.S. lavora in background.

    La GUI non viene aperta automaticamente.
    """

    SESSION_CLOSE_COMMANDS = {
        "basta",
        "grazie jarvis",
        "puoi dormire",
        "torna in attesa",
        "fine conversazione",
    }

    def __init__(
        self,
        assistant: Assistant,
    ) -> None:

        self._assistant = assistant

        self._wake_word = (
            WakeWordManager()
        )

        self._session = (
            WakeWordSession(
                timeout_seconds=8.0
            )
        )

        self._feedback = (
            FeedbackPlayer()
        )

        self._running = (
            threading.Event()
        )

        self._thread: (
            threading.Thread | None
        ) = None

    @property
    def enabled(
        self,
    ) -> bool:
        return (
            self._wake_word.enabled
        )

    def start(
        self,
    ) -> None:

        if (
            self._thread is not None
            and self._thread.is_alive()
        ):
            return

        self._running.set()

        self._thread = threading.Thread(
            target=self._run,
            name="JarvisBackgroundWake",
            daemon=True,
        )

        self._thread.start()

    def stop(
        self,
    ) -> None:

        self._running.clear()

        self._session.close()

        try:
            self._wake_word.reset()

        except Exception:
            pass

    def _run(
        self,
    ) -> None:

        while self._running.is_set():

            try:
                if not self._wake_word.enabled:
                    threading.Event().wait(
                        0.25
                    )

                    continue

                self._session.close()

                detected = (
                    self._wake_word
                    .wait_for_wake_word()
                )

                if not self._running.is_set():
                    break

                if not detected:
                    continue

                self._feedback.play(
                    FeedbackSound.WAKE
                )

                self._session.activate()

                self._feedback.play(
                    FeedbackSound.LISTENING
                )

                self._assistant.conversation.reply(
                    "Ti ascolto."
                )

                while (
                    self._running.is_set()
                    and self._session.is_active
                ):

                    remaining = (
                        self._session
                        .remaining_seconds()
                    )

                    if remaining <= 0:
                        self._session.close()

                        self._feedback.play(
                            FeedbackSound.STANDBY
                        )

                        break

                    command = (
                        self._assistant
                        .services
                        .audio
                        .listen(
                            timeout_seconds=remaining
                        )
                    )

                    command = (
                        command
                        .strip()
                        .lower()
                    )

                    if not command:
                        self._session.close()

                        self._feedback.play(
                            FeedbackSound.STANDBY
                        )

                        break

                    if (
                        command
                        in self.SESSION_CLOSE_COMMANDS
                    ):
                        self._session.close()

                        self._assistant.conversation.reply(
                            "Va bene."
                        )

                        self._feedback.play(
                            FeedbackSound.STANDBY
                        )

                        break

                    self._assistant.process_command(
                        command
                    )

                    if self._session.is_active:
                        self._session.refresh()

            except Exception as error:

                try:
                    self._assistant.services.logger.error(
                        "Errore Wake Word background: "
                        f"{error}"
                    )

                except Exception:
                    pass