from abc import ABC, abstractmethod
from typing import Any


class ContextSource(ABC):
    """
    Interfaccia comune di tutte le sorgenti dati.
    """

    @property
    @abstractmethod
    def source_name(self) -> str:
        ...

    @abstractmethod
    def get_data(self) -> Any:
        ...