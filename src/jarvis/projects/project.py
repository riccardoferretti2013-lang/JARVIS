from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Project:
    """
    Rappresenta un progetto gestito da J.A.R.V.I.S.
    """

    name: str
    description: str = ""
    path: str = ""
    is_active: bool = False
    project_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        clean_name = self.name.strip()
        clean_description = self.description.strip()
        clean_path = self.path.strip()

        if not clean_name:
            raise ValueError(
                "Il nome del progetto non può essere vuoto."
            )

        object.__setattr__(
            self,
            "name",
            clean_name,
        )

        object.__setattr__(
            self,
            "description",
            clean_description,
        )

        object.__setattr__(
            self,
            "path",
            clean_path,
        )