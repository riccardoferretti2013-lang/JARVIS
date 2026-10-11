from abc import ABC, abstractmethod

from ..context_block import ContextBlock


class ContextProvider(ABC):
    """
    Interfaccia comune di tutti i provider.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...

    @property
    def priority(self) -> int:
        return 50

    @abstractmethod
    def get_context(self) -> ContextBlock:
        ...