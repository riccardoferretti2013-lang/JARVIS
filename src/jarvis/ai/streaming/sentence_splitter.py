class SentenceSplitter:

    def __init__(self) -> None:

        self._buffer = ""

    def add(
        self,
        text: str,
    ) -> list[str]:

        self._buffer += text

        sentences = []

        while True:

            index = -1

            for symbol in ".!?":

                pos = self._buffer.find(symbol)

                if pos != -1:

                    if index == -1 or pos < index:
                        index = pos

            if index == -1:
                break

            sentence = (
                self._buffer[: index + 1]
                .strip()
            )

            if sentence:
                sentences.append(sentence)

            self._buffer = self._buffer[
                index + 1 :
            ]

        return sentences

    def flush(
        self,
    ) -> str:

        text = self._buffer.strip()

        self._buffer = ""

        return text