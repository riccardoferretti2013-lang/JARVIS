import re

from .contact import Contact
from .contact_manager import ContactManager


class ContactCommands:
    """
    Gestisce i comandi relativi ai contatti.
    """

    def __init__(
        self,
        manager: ContactManager | None = None,
    ) -> None:
        self._manager = (
            manager
            or ContactManager()
        )

    @property
    def manager(self) -> ContactManager:
        return self._manager

    def process(
        self,
        command: str,
    ) -> str | None:
        clean_command = command.strip()

        if not clean_command:
            return None

        processors = [
            self._process_create,
            self._process_phone,
            self._process_email,
            self._process_address,
            self._process_relationship,
            self._process_notes,
            self._process_details,
            self._process_delete,
        ]

        for processor in processors:
            response = processor(
                clean_command
            )

            if response is not None:
                return response

        lowered_command = clean_command.lower()

        if lowered_command in {
            "lista contatti",
            "elenco contatti",
            "mostra contatti",
        }:
            return self._contact_list_response()

        if lowered_command in {
            "numero contatti",
            "quanti contatti",
            "conteggio contatti",
        }:
            return self._contact_count_response()

        return None

    def _process_create(
        self,
        command: str,
    ) -> str | None:
        match = re.fullmatch(
            r"crea contatto\s+(.+)",
            command,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        name = self._clean_value(
            match.group(1)
        )

        if self._manager.exists(name):
            return (
                f"Il contatto '{name}' esiste già."
            )

        contact = self._manager.create(
            name=name
        )

        return (
            f"Contatto '{contact.name}' creato."
        )

    def _process_phone(
        self,
        command: str,
    ) -> str | None:
        match = re.fullmatch(
            (
                r"(?:telefono contatto|numero contatto)\s+"
                r"(.+?)\s*:?\s+"
                r"([+0-9][0-9 +().-]*)"
            ),
            command,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        return self._update_contact(
            name=self._clean_value(
                match.group(1)
            ),
            phone=self._clean_value(
                match.group(2)
            ),
            field_name="telefono",
        )

    def _process_email(
        self,
        command: str,
    ) -> str | None:
        match = re.fullmatch(
            (
                r"email contatto\s+"
                r"(.+?)\s*:?\s+"
                r"([A-Za-z0-9._%+-]+@"
                r"[A-Za-z0-9.-]+\.[A-Za-z]{2,})"
            ),
            command,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        return self._update_contact(
            name=self._clean_value(
                match.group(1)
            ),
            email=self._clean_value(
                match.group(2)
            ),
            field_name="email",
        )

    def _process_address(
        self,
        command: str,
    ) -> str | None:
        match = re.fullmatch(
            (
                r"(?:indirizzo contatto|"
                r"residenza contatto)\s+"
                r"(.+?)\s*:?\s+(.+)"
            ),
            command,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        return self._update_contact(
            name=self._clean_value(
                match.group(1)
            ),
            address=self._clean_value(
                match.group(2)
            ),
            field_name="indirizzo",
        )

    def _process_relationship(
        self,
        command: str,
    ) -> str | None:
        match = re.fullmatch(
            (
                r"(?:relazione contatto|"
                r"rapporto contatto)\s+"
                r"(.+?)\s*:?\s+(.+)"
            ),
            command,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        return self._update_contact(
            name=self._clean_value(
                match.group(1)
            ),
            relationship=self._clean_value(
                match.group(2)
            ),
            field_name="relazione",
        )

    def _process_notes(
        self,
        command: str,
    ) -> str | None:
        match = re.fullmatch(
            (
                r"(?:nota contatto|"
                r"note contatto)\s+"
                r"(.+?)\s*:?\s+(.+)"
            ),
            command,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        return self._update_contact(
            name=self._clean_value(
                match.group(1)
            ),
            notes=self._clean_value(
                match.group(2)
            ),
            field_name="note",
        )

    def _process_details(
        self,
        command: str,
    ) -> str | None:
        match = re.fullmatch(
            (
                r"(?:dettagli contatto|"
                r"informazioni contatto|"
                r"mostra contatto)\s+(.+)"
            ),
            command,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        name = self._clean_value(
            match.group(1)
        )

        contact = self._manager.get(
            name
        )

        if contact is None:
            return (
                f"Il contatto '{name}' non esiste."
            )

        return self._format_contact(
            contact
        )

    def _process_delete(
        self,
        command: str,
    ) -> str | None:
        match = re.fullmatch(
            (
                r"(?:elimina|cancella|rimuovi) "
                r"contatto\s+(.+)"
            ),
            command,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        name = self._clean_value(
            match.group(1)
        )

        deleted = self._manager.delete(
            name
        )

        if not deleted:
            return (
                f"Il contatto '{name}' non esiste."
            )

        return (
            f"Contatto '{name}' eliminato."
        )

    def _update_contact(
        self,
        name: str,
        phone: str | None = None,
        email: str | None = None,
        address: str | None = None,
        notes: str | None = None,
        relationship: str | None = None,
        field_name: str = "",
    ) -> str:
        current = self._manager.get(
            name
        )

        if current is None:
            return (
                f"Il contatto '{name}' non esiste."
            )

        updated = self._manager.create(
            name=current.name,
            phone=(
                phone
                if phone is not None
                else current.phone
            ),
            email=(
                email
                if email is not None
                else current.email
            ),
            address=(
                address
                if address is not None
                else current.address
            ),
            notes=(
                notes
                if notes is not None
                else current.notes
            ),
            relationship=(
                relationship
                if relationship is not None
                else current.relationship
            ),
        )

        if field_name:
            return (
                f"{field_name.capitalize()} del contatto "
                f"'{updated.name}' aggiornato."
            )

        return (
            f"Contatto '{updated.name}' aggiornato."
        )

    def _contact_list_response(self) -> str:
        contacts = self._manager.get_all()

        if not contacts:
            return "Non ci sono contatti."

        lines = [
            "Contatti disponibili:"
        ]

        for contact in contacts:
            lines.append(
                f"• {contact.name}"
            )

        return "\n".join(lines)

    def _contact_count_response(self) -> str:
        count = self._manager.count()

        if count == 0:
            return "Non ci sono contatti."

        if count == 1:
            return "C'è un contatto salvato."

        return (
            f"Ci sono {count} contatti salvati."
        )

    @staticmethod
    def _format_contact(
        contact: Contact,
    ) -> str:
        phone = (
            contact.phone
            or "non disponibile"
        )

        email = (
            contact.email
            or "non disponibile"
        )

        address = (
            contact.address
            or "non disponibile"
        )

        relationship = (
            contact.relationship
            or "non specificata"
        )

        notes = (
            contact.notes
            or "nessuna nota"
        )

        return (
            f"Contatto: {contact.name}\n"
            f"Telefono: {phone}\n"
            f"Email: {email}\n"
            f"Indirizzo: {address}\n"
            f"Relazione: {relationship}\n"
            f"Note: {notes}"
        )

    @staticmethod
    def _clean_value(
        value: str,
    ) -> str:
        return (
            value
            .strip()
            .rstrip(".,!?")
        )