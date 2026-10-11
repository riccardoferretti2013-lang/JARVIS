from .contact import Contact
from .contact_repository import ContactRepository


class ContactManager:
    """
    Gestisce la logica dei contatti.
    """

    def __init__(
        self,
        repository: ContactRepository | None = None,
    ) -> None:
        self._repository = (
            repository
            or ContactRepository()
        )

    @property
    def repository(
        self,
    ) -> ContactRepository:
        return self._repository

    def create(
        self,
        name: str,
        phone: str = "",
        email: str = "",
        address: str = "",
        notes: str = "",
        relationship: str = "",
    ) -> Contact:
        contact = Contact(
            name=name,
            phone=phone,
            email=email,
            address=address,
            notes=notes,
            relationship=relationship,
        )

        return self._repository.save(
            contact
        )

    def exists(
        self,
        name: str,
    ) -> bool:
        return (
            self._repository.get_by_name(
                name
            )
            is not None
        )

    def get(
        self,
        name: str,
    ) -> Contact | None:
        return self._repository.get_by_name(
            name
        )

    def get_all(
        self,
    ) -> list[Contact]:
        return self._repository.get_all()

    def count(
        self,
    ) -> int:
        return self._repository.count()

    def delete(
        self,
        name: str,
    ) -> bool:
        return self._repository.delete(
            name
        )