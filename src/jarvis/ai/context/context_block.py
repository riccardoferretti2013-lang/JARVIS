from dataclasses import dataclass, field

from ..provider import Message


@dataclass(slots=True)
class ContextBlock:
    """
    Blocco di contesto prodotto da un ContextProvider.
    """

    name: str
    priority: int
    messages: list[Message] = field(default_factory=list)
    enabled: bool = True