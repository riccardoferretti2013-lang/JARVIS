from collections.abc import Iterator

from ollama import Client, ResponseError

from .ai_response import AIResponse, ToolCall
from .provider import AIProvider, Message, ToolDefinition


class OllamaProvider(AIProvider):
    """
    Provider AI locale basato su Ollama.

    Include:
    - timeout HTTP;
    - limite massimo di token generati;
    - supporto streaming;
    - supporto tool calling.
    """

    def __init__(
        self,
        model: str = "qwen3:4b-instruct",
        host: str = "http://localhost:11434",
        timeout_seconds: float = 60.0,
        max_tokens: int = 256,
    ) -> None:

        self._model = model
        self._timeout_seconds = timeout_seconds
        self._max_tokens = max_tokens

        self._client = Client(
            host=host,
            timeout=timeout_seconds,
        )

    @property
    def provider_name(self) -> str:
        return "Ollama"

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def timeout_seconds(self) -> float:
        return self._timeout_seconds

    @property
    def max_tokens(self) -> int:
        return self._max_tokens

    def is_available(self) -> bool:

        try:
            self._client.list()
            return True

        except Exception:
            return False

    def generate(
        self,
        messages: list[Message],
    ) -> str:

        if not messages:
            return "La conversazione è vuota."

        try:

            response = self._client.chat(
                model=self._model,
                messages=messages,
                stream=False,
                think=False,
                options={
                    "num_predict": self._max_tokens,
                },
            )

            return (
                response.message.content or ""
            ).strip()

        except ResponseError as error:

            return (
                f"Errore Ollama: "
                f"{error.error}"
            )

        except Exception as error:

            return (
                "Errore imprevisto di Ollama: "
                f"{error}"
            )

    def generate_stream(
        self,
        messages: list[Message],
    ) -> Iterator[str]:

        if not messages:
            return

        try:

            stream = self._client.chat(
                model=self._model,
                messages=messages,
                stream=True,
                think=False,
                options={
                    "num_predict": self._max_tokens,
                },
            )

            for chunk in stream:

                text = (
                    chunk.message.content
                    or ""
                )

                if text:
                    yield text

        except ResponseError as error:

            yield (
                f"Errore Ollama: "
                f"{error.error}"
            )

        except Exception as error:

            yield (
                "Errore imprevisto di Ollama: "
                f"{error}"
            )

    def generate_with_tools(
        self,
        messages: list[Message],
        tools: list[ToolDefinition],
    ) -> AIResponse:

        if not messages:

            return AIResponse(
                content="La conversazione è vuota."
            )

        try:

            response = self._client.chat(
                model=self._model,
                messages=messages,
                tools=tools,
                stream=False,
                think=False,
                options={
                    "num_predict": self._max_tokens,
                },
            )

            tool_calls: list[ToolCall] = []

            for tool_call in (
                response.message.tool_calls
                or []
            ):

                function = (
                    tool_call.function
                )

                tool_calls.append(
                    ToolCall(
                        name=function.name,
                        arguments=dict(
                            function.arguments
                            or {}
                        ),
                    )
                )

            return AIResponse(
                content=(
                    response.message.content
                    or ""
                ).strip(),
                tool_calls=tool_calls,
            )

        except ResponseError as error:

            return AIResponse(
                content=(
                    f"Errore Ollama: "
                    f"{error.error}"
                )
            )

        except Exception as error:

            return AIResponse(
                content=(
                    "Errore imprevisto di Ollama: "
                    f"{error}"
                )
            )