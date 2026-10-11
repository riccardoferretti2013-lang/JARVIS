import sqlite3
from datetime import datetime
from pathlib import Path

from .project import Project


class ProjectRepository:
    """
    Gestisce il salvataggio permanente dei progetti.
    """

    DEFAULT_DATABASE_PATH = Path(
        "data/projects/jarvis_projects.db"
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
        project: Project,
    ) -> Project:
        now = datetime.now().isoformat()

        with self._connect() as connection:
            if project.is_active:
                connection.execute(
                    """
                    UPDATE projects
                    SET is_active = 0
                    """
                )

            connection.execute(
                """
                INSERT INTO projects (
                    name,
                    description,
                    path,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(name)
                DO UPDATE SET
                    description = excluded.description,
                    path = excluded.path,
                    is_active = excluded.is_active,
                    updated_at = excluded.updated_at
                """,
                (
                    project.name,
                    project.description,
                    project.path,
                    int(project.is_active),
                    now,
                    now,
                ),
            )

        saved_project = self.get_by_name(
            project.name
        )

        if saved_project is None:
            raise RuntimeError(
                "Impossibile rileggere il progetto salvato."
            )

        return saved_project

    def get_by_name(
        self,
        name: str,
    ) -> Project | None:
        clean_name = name.strip()

        if not clean_name:
            return None

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    name,
                    description,
                    path,
                    is_active,
                    created_at,
                    updated_at
                FROM projects
                WHERE LOWER(name) = LOWER(?)
                """,
                (clean_name,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_project(row)

    def get_active(self) -> Project | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    name,
                    description,
                    path,
                    is_active,
                    created_at,
                    updated_at
                FROM projects
                WHERE is_active = 1
                LIMIT 1
                """
            ).fetchone()

        if row is None:
            return None

        return self._row_to_project(row)

    def get_all(self) -> list[Project]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    name,
                    description,
                    path,
                    is_active,
                    created_at,
                    updated_at
                FROM projects
                ORDER BY
                    is_active DESC,
                    updated_at DESC,
                    name ASC
                """
            ).fetchall()

        return [
            self._row_to_project(row)
            for row in rows
        ]

    def set_active(
        self,
        name: str,
    ) -> Project | None:
        project = self.get_by_name(name)

        if project is None:
            return None

        now = datetime.now().isoformat()

        with self._connect() as connection:
            connection.execute(
                """
                UPDATE projects
                SET is_active = 0
                """
            )

            connection.execute(
                """
                UPDATE projects
                SET
                    is_active = 1,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    now,
                    project.project_id,
                ),
            )

        return self.get_by_name(
            project.name
        )

    def clear_active(self) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE projects
                SET
                    is_active = 0,
                    updated_at = ?
                WHERE is_active = 1
                """,
                (
                    datetime.now().isoformat(),
                ),
            )

        return cursor.rowcount > 0

    def update_description(
        self,
        name: str,
        description: str,
    ) -> Project | None:
        project = self.get_by_name(name)

        if project is None:
            return None

        with self._connect() as connection:
            connection.execute(
                """
                UPDATE projects
                SET
                    description = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    description.strip(),
                    datetime.now().isoformat(),
                    project.project_id,
                ),
            )

        return self.get_by_name(
            project.name
        )

    def update_path(
        self,
        name: str,
        path: str,
    ) -> Project | None:
        project = self.get_by_name(name)

        if project is None:
            return None

        with self._connect() as connection:
            connection.execute(
                """
                UPDATE projects
                SET
                    path = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    path.strip(),
                    datetime.now().isoformat(),
                    project.project_id,
                ),
            )

        return self.get_by_name(
            project.name
        )

    def delete(
        self,
        name: str,
    ) -> bool:
        project = self.get_by_name(name)

        if project is None:
            return False

        with self._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM projects
                WHERE id = ?
                """,
                (
                    project.project_id,
                ),
            )

        return cursor.rowcount > 0

    def count(self) -> int:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*)
                FROM projects
                """
            ).fetchone()

        return int(row[0]) if row else 0

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL DEFAULT '',
                    path TEXT NOT NULL DEFAULT '',
                    is_active INTEGER NOT NULL DEFAULT 0,
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
    def _row_to_project(
        row: sqlite3.Row,
    ) -> Project:
        return Project(
            project_id=int(row["id"]),
            name=str(row["name"]),
            description=str(row["description"]),
            path=str(row["path"]),
            is_active=bool(row["is_active"]),
            created_at=datetime.fromisoformat(
                str(row["created_at"])
            ),
            updated_at=datetime.fromisoformat(
                str(row["updated_at"])
            ),
        )