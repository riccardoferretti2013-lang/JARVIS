from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Agent:
    """
    Rappresenta un agente specializzato della AI Company di J.A.R.V.I.S.
    """

    agent_id: str
    name: str
    role: str
    department: str
    system_prompt: str

    description: str = ""

    preferred_provider: str | None = None
    preferred_model: str | None = None

    max_tokens: int = 256
    timeout_seconds: float = 60.0

    priority: int = 5

    use_local_model: bool = True

    enabled: bool = True

    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.agent_id = self.agent_id.strip()
        self.name = self.name.strip()
        self.role = self.role.strip()
        self.department = self.department.strip()
        self.system_prompt = self.system_prompt.strip()
        self.description = self.description.strip()

        if not self.agent_id:
            raise ValueError(
                "agent_id non può essere vuoto."
            )

        if not self.name:
            raise ValueError(
                "name non può essere vuoto."
            )

        if not self.role:
            raise ValueError(
                "role non può essere vuoto."
            )

        if not self.department:
            raise ValueError(
                "department non può essere vuoto."
            )

        if not self.system_prompt:
            raise ValueError(
                "system_prompt non può essere vuoto."
            )

        if self.max_tokens < 1:
            raise ValueError(
                "max_tokens deve essere almeno 1."
            )

        if self.timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds deve essere maggiore di 0."
            )

        if self.priority < 1:
            raise ValueError(
                "priority deve essere almeno 1."
            )

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False

    def is_available(self) -> bool:
        return self.enabled

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "department": self.department,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "preferred_provider": self.preferred_provider,
            "preferred_model": self.preferred_model,
            "max_tokens": self.max_tokens,
            "timeout_seconds": self.timeout_seconds,
            "priority": self.priority,
            "use_local_model": self.use_local_model,
            "enabled": self.enabled,
            "metadata": dict(self.metadata),
        }

    def __str__(self) -> str:
        status = (
            "ONLINE"
            if self.enabled
            else "OFFLINE"
        )

        provider = (
            self.preferred_provider
            or "default"
        )

        return (
            f"{self.name} "
            f"[{self.agent_id}] - "
            f"{self.role} / "
            f"{self.department} - "
            f"{status} - "
            f"provider={provider}"
        )