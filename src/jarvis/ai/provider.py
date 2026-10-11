from collections.abc import Iterator
from typing import Protocol, TypedDict, NotRequired, Any


class Message(TypedDict):
    role: str
    content: str


class ToolDefinition(TypedDict):
    type: str
    function: dict[str, Any]


class AIProvider(Protocol):

    def is_available(self) -> bool:
        ...

    def generate(
        self,
        messages: list[Message],
    ) -> str:
        ...

    def generate_stream(
        self,
        messages: list[Message],
    ) -> Iterator[str]:
        ...

    def generate_with_tools(
        self,
        messages: list[Message],
        tools: list[ToolDefinition],
    ):
        ...