from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class MemoryType(StrEnum):
    """
    Tipologie di ricordi gestiti da J.A.R.V.I.S.
    """

    PROFILE = "profile"
    PREFERENCE = "preference"
    PROJECT = "project"
    FACT = "fact"
    EXPERIENCE = "experience"


@dataclass(frozen=True)
class Memory:
    """
    Rappresenta un singolo ricordo permanente.
    """

    key: str
    value: str
    memory_type: MemoryType
    importance: int = 5
    created_at: datetime | None = None
    updated_at: datetime | None = None
    memory_id: int | None = None

    def __post_init__(self) -> None:
        clean_key = self.key.strip()
        clean_value = self.value.strip()

        if not clean_key:
            raise ValueError(
                "La chiave del ricordo non può essere vuota."
            )

        if not clean_value:
            raise ValueError(
                "Il valore del ricordo non può essere vuoto."
            )

        if not 1 <= self.importance <= 10:
            raise ValueError(
                "L'importanza deve essere compresa tra 1 e 10."
            )

        object.__setattr__(self, "key", clean_key)
        object.__setattr__(self, "value", clean_value)