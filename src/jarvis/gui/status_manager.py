from enum import Enum


class JarvisState(Enum):
    STARTING = "starting"
    READY = "ready"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    ERROR = "error"


class StatusManager:

    LABELS = {
        JarvisState.STARTING: "AVVIO SISTEMI",
        JarvisState.READY: "TUTTO OPERATIVO",
        JarvisState.LISTENING: "IN ASCOLTO",
        JarvisState.THINKING: "ELABORAZIONE",
        JarvisState.SPEAKING: "RISPOSTA ATTIVA",
        JarvisState.ERROR: "ERRORE SISTEMA",
    }

    COLORS = {
        JarvisState.STARTING: "#FFC857",
        JarvisState.READY: "#00E59B",
        JarvisState.LISTENING: "#00E5FF",
        JarvisState.THINKING: "#8B7CFF",
        JarvisState.SPEAKING: "#00A8FF",
        JarvisState.ERROR: "#FF4D6D",
    }

    @classmethod
    def label(
        cls,
        state: JarvisState,
    ) -> str:
        return cls.LABELS[
            state
        ]

    @classmethod
    def color(
        cls,
        state: JarvisState,
    ) -> str:
        return cls.COLORS[
            state
        ]