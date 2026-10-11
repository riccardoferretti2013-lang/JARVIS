from dataclasses import dataclass


@dataclass(slots=True)
class StreamChunk:
    """
    Singolo blocco dello streaming.
    """

    text: str
    is_last: bool = False