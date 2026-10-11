from collections.abc import Iterator

from ollama import Client, ResponseError

from .ai_response import AIResponse, ToolCall
from .provider import AIProvider, Message, ToolDefinition


class OllamaProvider(AIProvider):
    """
    Provider AI locale basato su Ollama.
    """

    def __init__(
        self,
        model: str = "qwen3:4b-instruct",
        host: str = "http://localhost:11434",
    ) -> None:

        self._model = model
        self._client = Client(host=host)

    @property
    def provider_name(self) -> str:
        return "Ollama"

    @property
    def model_name(self) -> str:
        return self._model

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
            )

            return (
                response.message.content or ""
            ).strip()

        except ResponseError as error:
            return f"Errore Ollama: {error.error}"

        except Exception as error:
            return f"Errore imprevisto di Ollama: {error}"

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
                f"Errore Ollama: {error.error}"
            )

        except Exception as error:

            yield (
                f"Errore imprevisto di Ollama: {error}"
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
            )

            tool_calls: list[ToolCall] = []

            for tool_call in (
                response.message.tool_calls
                or []
            ):

                function = tool_call.function

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
                content=f"Errore Ollama: {error.error}"
            )

        except Exception as error:

            return AIResponse(
                content=f"Errore imprevisto di Ollama: {error}"
            )