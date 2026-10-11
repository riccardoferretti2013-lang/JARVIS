from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Contact:
    """
    Rappresenta un contatto conosciuto da J.A.R.V.I.S.
    """

    name: str
    phone: str = ""
    email: str = ""
    address: str = ""
    notes: str = ""
    relationship: str = ""

    contact_id: int | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:

        clean_name = self.name.strip()

        if not clean_name:
            raise ValueError(
                "Il nome del contatto non può essere vuoto."
            )

        object.__setattr__(
            self,
            "name",
            clean_name,
        )

        object.__setattr__(
            self,
            "phone",
            self.phone.strip(),
        )

        object.__setattr__(
            self,
            "email",
            self.email.strip(),
        )

        object.__setattr__(
            self,
            "address",
            self.address.strip(),
        )

        object.__setattr__(
            self,
            "notes",
            self.notes.strip(),
        )

        object.__setattr__(
            self,
            "relationship",
            self.relationship.strip(),
        )