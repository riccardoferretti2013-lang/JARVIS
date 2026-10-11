from enum import Enum


class FeedbackSound(str, Enum):
    """
    Tipi di feedback sonoro disponibili.
    """

    WAKE = "wake"
    LISTENING = "listening"
    SUCCESS = "success"
    TIMEOUT = "timeout"
    ERROR = "error"
    STANDBY = "standby"