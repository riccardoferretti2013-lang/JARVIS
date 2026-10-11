from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class PreferredApplication:
    """
    Rappresenta un'applicazione preferita dell'utente.
    """

    category: str
    application_name: str
    executable_path: str = ""
    application_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        clean_category = self.category.strip().lower()
        clean_name = self.application_name.strip()
        clean_path = self.executable_path.strip()

        if not clean_category:
            raise ValueError(
                "La categoria non può essere vuota."
            )

        if not clean_name:
            raise ValueError(
                "Il nome dell'applicazione non può essere vuoto."
            )

        object.__setattr__(
            self,
            "category",
            clean_category,
        )

        object.__setattr__(
            self,
            "application_name",
            clean_name,
        )

        object.__setattr__(
            self,
            "executable_path",
            clean_path,
        )