import sqlite3
from datetime import datetime
from pathlib import Path

from .contact import Contact


class ContactRepository:
    """
    Gestisce il salvataggio permanente dei contatti.
    """

    DEFAULT_DATABASE_PATH = Path(
        "data/contacts/jarvis_contacts.db"
    )

    def __init__(
        self,
        database_path: str | Path | None = None,
    ) -> None:
        self._database_path = Path(
            database_path
            or self.DEFAULT_DATABASE_PATH
        )

        self._database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_database()

    @property
    def database_path(self) -> Path:
        return self._database_path

    def save(
        self,
        contact: Contact,
    ) -> Contact:
        now = datetime.now().isoformat()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO contacts (
                    name,
                    phone,
                    email,
                    address,
                    notes,
                    relationship,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name)
                DO UPDATE SET
                    phone = excluded.phone,
                    email = excluded.email,
                    address = excluded.address,
                    notes = excluded.notes,
                    relationship = excluded.relationship,
                    updated_at = excluded.updated_at
                """,
                (
                    contact.name,
                    contact.phone,
                    contact.email,
                    contact.address,
                    contact.notes,
                    contact.relationship,
                    now,
                    now,
                ),
            )

        saved_contact = self.get_by_name(
            contact.name
        )

        if saved_contact is None:
            raise RuntimeError(
                "Impossibile rileggere il contatto salvato."
            )

        return saved_contact

    def get_by_name(
        self,
        name: str,
    ) -> Contact | None:
        clean_name = name.strip()

        if not clean_name:
            return None

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    name,
                    phone,
                    email,
                    address,
                    notes,
                    relationship,
                    created_at,
                    updated_at
                FROM contacts
                WHERE LOWER(name) = LOWER(?)
                """,
                (clean_name,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_contact(row)

    def get_all(self) -> list[Contact]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    name,
                    phone,
                    email,
                    address,
                    notes,
                    relationship,
                    created_at,
                    updated_at
                FROM contacts
                ORDER BY name ASC
                """
            ).fetchall()

        return [
            self._row_to_contact(row)
            for row in rows
        ]

    def delete(
        self,
        name: str,
    ) -> bool:
        contact = self.get_by_name(name)

        if contact is None:
            return False

        with self._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM contacts
                WHERE id = ?
                """,
                (
                    contact.contact_id,
                ),
            )

        return cursor.rowcount > 0

    def count(self) -> int:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*)
                FROM contacts
                """
            ).fetchone()

        return int(row[0]) if row else 0

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    phone TEXT NOT NULL DEFAULT '',
                    email TEXT NOT NULL DEFAULT '',
                    address TEXT NOT NULL DEFAULT '',
                    notes TEXT NOT NULL DEFAULT '',
                    relationship TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self._database_path
        )

        connection.row_factory = sqlite3.Row

        return connection

    @staticmethod
    def _row_to_contact(
        row: sqlite3.Row,
    ) -> Contact:
        return Contact(
            contact_id=int(row["id"]),
            name=str(row["name"]),
            phone=str(row["phone"]),
            email=str(row["email"]),
            address=str(row["address"]),
            notes=str(row["notes"]),
            relationship=str(row["relationship"]),
            created_at=datetime.fromisoformat(
                str(row["created_at"])
            ),
            updated_at=datetime.fromisoformat(
                str(row["updated_at"])
            ),
        )