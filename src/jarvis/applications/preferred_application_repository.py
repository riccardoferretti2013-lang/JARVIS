import sqlite3
from datetime import datetime
from pathlib import Path

from .preferred_application import PreferredApplication


class PreferredApplicationRepository:
    """
    Gestisce il salvataggio permanente
    delle applicazioni preferite.
    """

    DEFAULT_DATABASE_PATH = Path(
        "data/applications/jarvis_applications.db"
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
        application: PreferredApplication,
    ) -> PreferredApplication:
        now = datetime.now().isoformat()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO preferred_applications (
                    category,
                    application_name,
                    executable_path,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(category)
                DO UPDATE SET
                    application_name = excluded.application_name,
                    executable_path = excluded.executable_path,
                    updated_at = excluded.updated_at
                """,
                (
                    application.category,
                    application.application_name,
                    application.executable_path,
                    now,
                    now,
                ),
            )

        saved_application = self.get_by_category(
            application.category
        )

        if saved_application is None:
            raise RuntimeError(
                "Impossibile rileggere "
                "l'applicazione preferita salvata."
            )

        return saved_application

    def get_by_category(
        self,
        category: str,
    ) -> PreferredApplication | None:
        clean_category = category.strip().lower()

        if not clean_category:
            return None

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    category,
                    application_name,
                    executable_path,
                    created_at,
                    updated_at
                FROM preferred_applications
                WHERE LOWER(category) = LOWER(?)
                """,
                (clean_category,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_application(row)

    def get_all(
        self,
    ) -> list[PreferredApplication]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    category,
                    application_name,
                    executable_path,
                    created_at,
                    updated_at
                FROM preferred_applications
                ORDER BY category ASC
                """
            ).fetchall()

        return [
            self._row_to_application(row)
            for row in rows
        ]

    def update_path(
        self,
        category: str,
        executable_path: str,
    ) -> PreferredApplication | None:
        application = self.get_by_category(
            category
        )

        if application is None:
            return None

        with self._connect() as connection:
            connection.execute(
                """
                UPDATE preferred_applications
                SET
                    executable_path = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    executable_path.strip(),
                    datetime.now().isoformat(),
                    application.application_id,
                ),
            )

        return self.get_by_category(
            application.category
        )

    def delete(
        self,
        category: str,
    ) -> bool:
        application = self.get_by_category(
            category
        )

        if application is None:
            return False

        with self._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM preferred_applications
                WHERE id = ?
                """,
                (
                    application.application_id,
                ),
            )

        return cursor.rowcount > 0

    def count(self) -> int:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*)
                FROM preferred_applications
                """
            ).fetchone()

        return int(row[0]) if row else 0

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS preferred_applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL UNIQUE,
                    application_name TEXT NOT NULL,
                    executable_path TEXT NOT NULL DEFAULT '',
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
    def _row_to_application(
        row: sqlite3.Row,
    ) -> PreferredApplication:
        return PreferredApplication(
            application_id=int(row["id"]),
            category=str(row["category"]),
            application_name=str(
                row["application_name"]
            ),
            executable_path=str(
                row["executable_path"]
            ),
            created_at=datetime.fromisoformat(
                str(row["created_at"])
            ),
            updated_at=datetime.fromisoformat(
                str(row["updated_at"])
            ),
        )