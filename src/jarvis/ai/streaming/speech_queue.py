from queue import Empty, Queue
from threading import Thread


class SpeechQueue:

    def __init__(
        self,
        speaker,
    ) -> None:

        self._speaker = speaker

        self._queue: Queue[str] = Queue()

        self._thread = Thread(
            target=self._worker,
            daemon=True,
        )

        self._thread.start()

    def speak(
        self,
        text: str,
    ) -> None:

        text = text.strip()

        if text:
            self._queue.put(text)

    def clear(
        self,
    ) -> None:
        """
        Elimina tutte le frasi ancora
        in attesa di essere pronunciate.
        """

        while True:
            try:
                self._queue.get_nowait()

            except Empty:
                break

            else:
                self._queue.task_done()

    def _worker(
        self,
    ) -> None:

        while True:

            sentence = self._queue.get()

            try:
                self._speaker.speak(
                    sentence
                )

            finally:
                self._queue.task_done()