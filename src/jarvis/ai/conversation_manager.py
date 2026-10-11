from copy import deepcopy
from typing import Any

from .provider import Message


class ConversationManager:
    """
    Gestisce la cronologia temporanea
    della conversazione AI.
    """

    def __init__(
        self,
        max_messages: int = 30,
    ) -> None:
        if max_messages < 4:
            raise ValueError(
                "max_messages deve essere almeno 4."
            )

        self._max_messages = max_messages
        self._messages: list[Message] = []

    @property
    def max_messages(self) -> int:
        return self._max_messages

    def add_message(
        self,
        message: Message,
    ) -> None:
        role = str(
            message.get(
                "role",
                "",
            )
        ).strip()

        if not role:
            raise ValueError(
                "Il messaggio deve contenere un ruolo."
            )

        self._messages.append(
            deepcopy(message)
        )

        self._trim_history()

    def add_user_message(
        self,
        content: str,
    ) -> None:
        clean_content = content.strip()

        if not clean_content:
            return

        self.add_message(
            {
                "role": "user",
                "content": clean_content,
            }
        )

    def add_assistant_message(
        self,
        content: str,
    ) -> None:
        clean_content = content.strip()

        if not clean_content:
            return

        self.add_message(
            {
                "role": "assistant",
                "content": clean_content,
            }
        )

    def add_assistant_tool_calls(
        self,
        tool_calls: list[dict[str, Any]],
        content: str = "",
    ) -> None:
        if not tool_calls:
            return

        self.add_message(
            {
                "role": "assistant",
                "content": content.strip(),
                "tool_calls": deepcopy(
                    tool_calls
                ),
            }
        )

    def add_tool_result(
        self,
        tool_name: str,
        content: str,
    ) -> None:
        clean_name = tool_name.strip()
        clean_content = content.strip()

        if not clean_name:
            raise ValueError(
                "Il nome del tool non può essere vuoto."
            )

        self.add_message(
            {
                "role": "tool",
                "tool_name": clean_name,
                "content": clean_content,
            }
        )

    def get_messages(
        self,
    ) -> list[Message]:
        return deepcopy(
            self._messages
        )

    def replace_messages(
        self,
        messages: list[Message],
    ) -> None:
        """
        Sostituisce la cronologia corrente.

        Utilizzato dal sistema dei riassunti
        per mantenere soltanto i messaggi recenti.
        """

        valid_messages: list[Message] = []

        for message in messages:
            role = str(
                message.get(
                    "role",
                    "",
                )
            ).strip()

            if not role:
                continue

            valid_messages.append(
                deepcopy(message)
            )

        self._messages = valid_messages

        self._trim_history()

    def clear(self) -> None:
        self._messages.clear()

    def message_count(self) -> int:
        return len(
            self._messages
        )

    def is_empty(self) -> bool:
        return not self._messages

    def _trim_history(self) -> None:
        while (
            len(self._messages)
            > self._max_messages
        ):
            self._messages.pop(0)

        while (
            self._messages
            and self._messages[0].get("role")
            == "tool"
        ):
            self._messages.pop(0)