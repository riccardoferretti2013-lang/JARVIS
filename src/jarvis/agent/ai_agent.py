from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from ..ai.ai_response import AIResponse, ToolCall
from ..ai.ai_service import AIService
from ..tools.tool_executor import ToolExecutor


class AIAgent:

    def __init__(
        self,
        ai_service: AIService | None = None,
        tool_executor: ToolExecutor | None = None,
        max_iterations: int = 5,
    ) -> None:

        if max_iterations < 1:
            raise ValueError(
                "max_iterations deve essere almeno 1."
            )

        self._ai = ai_service or AIService()
        self._executor = tool_executor or ToolExecutor()
        self._max_iterations = max_iterations

    @property
    def ai(self) -> AIService:
        return self._ai

    def process(
        self,
        message: str,
    ) -> str:

        return self._run(message)

    def process_stream(
        self,
        message: str,
    ) -> Iterator[str]:

        if not message.strip():
            yield "Non hai inserito nessun messaggio."
            return

        if not self._ai.is_available():
            yield (
                "Il sistema AI non è disponibile."
            )
            return

        yield from self._ai.generate_stream(
            message
        )

    def _run(
        self,
        message: str,
    ) -> str:

        clean_message = message.strip()

        if not clean_message:
            return "Non hai inserito nessun messaggio."

        if not self._ai.is_available():
            return (
                "Il sistema di intelligenza artificiale "
                "non è disponibile."
            )

        available_tools = (
            self._executor.available_tools()
        )

        response = (
            self._ai.generate_with_tools(
                message=clean_message,
                tools=available_tools,
            )
        )

        for _ in range(self._max_iterations):

            if not response.has_tool_calls:
                return self._finalize_response(
                    response
                )

            self._register_tool_calls(
                response
            )

            for tool_call in response.tool_calls:
                self._execute_and_register_tool(
                    tool_call
                )

            response = (
                self._ai.continue_with_tools(
                    tools=available_tools
                )
            )

        final_message = (
            "Numero massimo di iterazioni raggiunto."
        )

        self._ai.add_assistant_message(
            final_message
        )

        return final_message

    def _register_tool_calls(
        self,
        response: AIResponse,
    ) -> None:

        serialized = [
            self._serialize_tool_call(tc)
            for tc in response.tool_calls
        ]

        self._ai.add_assistant_tool_calls(
            tool_calls=serialized,
            content=response.content,
        )

    def _execute_and_register_tool(
        self,
        tool_call: ToolCall,
    ) -> None:

        result = self._executor.execute_call(
            tool_call
        )

        content = (
            result.message.strip()
            or "Nessun risultato."
        )

        self._ai.add_tool_result(
            tool_name=tool_call.name,
            content=content,
        )

    def _finalize_response(
        self,
        response: AIResponse,
    ) -> str:

        content = (
            response.content.strip()
            or "Nessuna risposta."
        )

        self._ai.add_assistant_message(
            content
        )

        return content

    @staticmethod
    def _serialize_tool_call(
        tool_call: ToolCall,
    ) -> dict[str, Any]:

        return {
            "type": "function",
            "function": {
                "name": tool_call.name,
                "arguments": tool_call.arguments,
            },
        }