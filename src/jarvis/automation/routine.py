from abc import ABC, abstractmethod


class Routine(ABC):
    """
    Classe base per tutte le automazioni
    di J.A.R.V.I.S.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def matches(
        self,
        command: str,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def execute(self) -> str:
        raise NotImplementedError