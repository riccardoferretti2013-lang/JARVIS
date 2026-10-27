
from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from .ai_response import AIResponse
from .provider import (
    AIProvider,
    Message,
    ToolDefinition,
)


# =============================================
# CONFIGURAZIONE
# =============================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_PATH)


class OpenAIProvider(AIProvider):
    """
    Provider OpenAI per J.A.R.V.I.S.

    Utilizza la Responses API.

    Funzionalita:
    - Generazione testuale
    - Streaming
    - Diagnostica delle risposte vuote
    - Gestione esplicita degli errori
    - Configurazione per singolo agente
    - Compatibilita con AI Company
    """

    def __init__(
        self,
        model: str | None = None,
        max_tokens: int = 512,
        timeout_seconds: float = 60.0,
    ) -> None:

        self._api_key = (
            os.getenv("OPENAI_API_KEY", "").strip()
        )

        self._model = (
            model
            or os.getenv("OPENAI_AGENT_MODEL", "").strip()
            or "gpt-5-mini"
        )

        self._max_tokens = max_tokens
        self._timeout_seconds = timeout_seconds

        self._client: OpenAI | None = None

        if self._api_key:
            self._client = OpenAI(
                api_key=self._api_key,
                timeout=self._timeout_seconds,
            )

    # =============================================
    # PROPRIETA
    # =============================================

    @property
    def provider_name(self) -> str:
        return "OpenAI"

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def max_tokens(self) -> int:
        return self._max_tokens

    @property
    def timeout_seconds(self) -> float:
        return self._timeout_seconds

    # =============================================
    # DISPONIBILITA
    # =============================================

    def is_available(self) -> bool:
        """
        Verifica la configurazione locale.

        Non esegue una richiesta API.
        """
        return (
            bool(self._api_key)
            and self._client is not None
        )

    # =============================================
    # PREPARAZIONE MESSAGGI
    # =============================================

    @staticmethod
    def _prepare_messages(
        messages: list[Message],
    ) -> tuple[str | None, list[dict]]:

        if not messages:
            raise ValueError(
                "La conversazione e vuota."
            )

        system_parts: list[str] = []
        input_messages: list[dict] = []

        for message in messages:

            role = message.get("role", "user")
            content = message.get("content", "")

            if role in {"system", "developer"}:
                if content:
                    system_parts.append(str(content))
                continue

            if role not in {"user", "assistant"}:
                raise ValueError(
                    f"Ruolo messaggio non supportato: {role}"
                )

            input_messages.append({
                "role": role,
                "content": content,
            })

        if not input_messages:
            raise ValueError(
                "Nessun messaggio utente o assistant."
            )

        instructions = (
            "\n\n".join(system_parts).strip()
            or None
        )

        return instructions, input_messages

    # =============================================
    # DIAGNOSTICA RISPOSTE VUOTE
    # =============================================

    def _check_response(
        self,
        response,
    ) -> str:

        text = (
            getattr(response, "output_text", None)
            or ""
        ).strip()

        if text:
            return text

        status = getattr(
            response,
            "status",
            "unknown",
        )

        incomplete = getattr(
            response,
            "incomplete_details",
            None,
        )

        usage = getattr(
            response,
            "usage",
            None,
        )

        output_tokens = getattr(
            usage,
            "output_tokens",
            None,
        )

        details = getattr(
            usage,
            "output_tokens_details",
            None,
        )

        reasoning_tokens = getattr(
            details,
            "reasoning_tokens",
            None,
        )

        raise RuntimeError(
            "OpenAI ha restituito una risposta "
            "senza testo. "
            f"Modello: {self._model}; "
            f"Stato: {status}; "
            f"Dettagli incompletezza: {incomplete}; "
            f"Limite output: {self._max_tokens}; "
            f"Token output: {output_tokens}; "
            f"Token ragionamento: {reasoning_tokens}."
        )

    # =============================================
    # GENERAZIONE TESTUALE
    # =============================================

    def generate(
        self,
        messages: list[Message],
    ) -> str:

        if self._client is None:
            raise RuntimeError(
                "OpenAI non configurato: "
                "controlla OPENAI_API_KEY nel .env."
            )

        instructions, input_messages = (
            self._prepare_messages(messages)
        )

        response = self._client.responses.create(
            model=self._model,
            instructions=instructions,
            input=input_messages,
            max_output_tokens=self._max_tokens,
        )

        return self._check_response(response)

    # =============================================
    # GENERAZIONE STREAMING
    # =============================================

    def generate_stream(
        self,
        messages: list[Message],
    ) -> Iterator[str]:

        if self._client is None:
            raise RuntimeError(
                "OpenAI non configurato: "
                "controlla OPENAI_API_KEY nel .env."
            )

        instructions, input_messages = (
            self._prepare_messages(messages)
        )

        with self._client.responses.stream(
            model=self._model,
            instructions=instructions,
            input=input_messages,
            max_output_tokens=self._max_tokens,
        ) as stream:

            received_text = False

            for event in stream:

                if (
                    event.type
                    == "response.output_text.delta"
                ):

                    delta = getattr(
                        event,
                        "delta",
                        "",
                    )

                    if delta:
                        received_text = True
                        yield delta

            final_response = stream.get_final_response()

            if not received_text:
                self._check_response(final_response)

    # =============================================
    # TOOL CALLING
    # =============================================

    def generate_with_tools(
        self,
        messages: list[Message],
        tools: list[ToolDefinition],
    ) -> AIResponse:
        """
        Compatibilita con l'interfaccia AIProvider.

        Il tool calling OpenAI non e ancora
        implementato in questa classe.

        Nessun tool viene eseguito.
        """

        if tools:
            raise NotImplementedError(
                "Tool calling OpenAI non ancora "
                "implementato in OpenAIProvider."
            )

        response = self.generate(messages)

        return AIResponse(
            content=response
        )
