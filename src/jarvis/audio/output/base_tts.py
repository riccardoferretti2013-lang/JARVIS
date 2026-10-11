from abc import ABC, abstractmethod


class BaseTTS(ABC):
    """
    Interfaccia comune per tutti i motori
    di sintesi vocale di J.A.R.V.I.S.
    """

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """
        Restituisce il nome del motore vocale.
        """

        raise NotImplementedError

    @abstractmethod
    def speak(self, text: str) -> None:
        """
        Pronuncia il testo ricevuto.
        """

        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        """
        Interrompe la riproduzione vocale corrente.
        """

        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """
        Verifica che il motore vocale sia disponibile.
        """

        raise NotImplementedError