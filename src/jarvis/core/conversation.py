from collections.abc import (
    Callable,
    Iterable,
)
from threading import Event

from ..ai.streaming import (
    SentenceSplitter,
    SpeechQueue,
)
from ..services.service_manager import (
    ServiceManager,
)


ConversationCallback = Callable[
    [str, str],
    None,
]


class Conversation:
    """
    Gestisce l'interazione testuale
    e vocale con l'utente.
    """

    def __init__(
        self,
        services: ServiceManager,
    ) -> None:
        self.services = services

        self._speech_queue = SpeechQueue(
            self.services.audio
        )

        self._cancel_response = Event()

        self._response_active = Event()

        self._output_callback: (
            ConversationCallback | None
        ) = None

    @property
    def response_active(
        self,
    ) -> bool:
        return self._response_active.is_set()

    def set_output_callback(
        self,
        callback: ConversationCallback | None,
    ) -> None:
        """
        Permette alla GUI di ricevere
        messaggi e streaming.
        """

        self._output_callback = callback

    def _emit(
        self,
        event: str,
        text: str = "",
    ) -> None:
        if self._output_callback is None:
            return

        try:
            self._output_callback(
                event,
                text,
            )

        except Exception:
            pass

    def listen(
        self,
        timeout_seconds: float | None = None,
    ) -> str:
        user_input = input(
            "\nScrivi un comando oppure "
            "premi INVIO per parlare:\n"
            "Tu: "
        ).strip()

        if user_input:
            return user_input

        return self.services.audio.listen(
            timeout_seconds=timeout_seconds
        )

    def cancel_current_response(
        self,
    ) -> bool:
        if (
            not self._response_active.is_set()
            and not self.services.audio.is_speaking
        ):
            return False

        self._cancel_response.set()

        self._speech_queue.clear()

        self.services.audio.stop_speaking()

        return True

    def reply(
        self,
        message: str,
    ) -> None:
        clean = message.strip()

        if not clean:
            return

        self._cancel_response.clear()
        self._response_active.set()

        try:
            print(
                f"J.A.R.V.I.S.: {clean}"
            )

            self._emit(
                "message",
                clean,
            )

            if self._cancel_response.is_set():
                return

            self.services.audio.speak(
                clean
            )

        finally:
            self._response_active.clear()

    def reply_stream(
        self,
        stream: Iterable[str],
    ) -> str:
        splitter = SentenceSplitter()

        complete = ""

        self._cancel_response.clear()
        self._response_active.set()

        print(
            "J.A.R.V.I.S.: ",
            end="",
            flush=True,
        )

        self._emit(
            "stream_start",
            "",
        )

        try:
            for chunk in stream:

                if self._cancel_response.is_set():
                    break

                if not chunk:
                    continue

                print(
                    chunk,
                    end="",
                    flush=True,
                )

                complete += chunk

                self._emit(
                    "stream_chunk",
                    chunk,
                )

                for sentence in splitter.add(
                    chunk
                ):
                    if self._cancel_response.is_set():
                        break

                    self._speech_queue.speak(
                        sentence
                    )

                if self._cancel_response.is_set():
                    break

            if not self._cancel_response.is_set():
                tail = splitter.flush()

                if tail:
                    self._speech_queue.speak(
                        tail
                    )

        except Exception as error:
            if not self._cancel_response.is_set():
                self.services.logger.error(
                    f"Errore streaming: {error}"
                )

        finally:
            if self._cancel_response.is_set():

                self._speech_queue.clear()

                self.services.audio.stop_speaking()

                close_method = getattr(
                    stream,
                    "close",
                    None,
                )

                if callable(
                    close_method
                ):
                    try:
                        close_method()

                    except Exception:
                        pass

            self._response_active.clear()

            self._emit(
                "stream_end",
                "",
            )

            print()

        return complete.strip()