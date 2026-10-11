import sqlite3
from datetime import datetime
from pathlib import Path

from .memory import Memory, MemoryType


class MemoryRepository:
    """
    Gestisce il salvataggio permanente dei ricordi tramite SQLite.
    """

    DEFAULT_DATABASE_PATH = Path("data/memory/jarvis_memory.db")

    def __init__(
        self,
        database_path: str | Path | None = None,
    ) -> None:
        self._database_path = Path(
            database_path or self.DEFAULT_DATABASE_PATH
        )

        self._database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_database()

    @property
    def database_path(self) -> Path:
        return self._database_path

    def save(self, memory: Memory) -> Memory:
        """
        Salva un nuovo ricordo oppure aggiorna quello
        con la stessa chiave e tipologia.
        """

        now = datetime.now()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO memories (
                    key,
                    value,
                    memory_type,
                    importance,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(key, memory_type)
                DO UPDATE SET
                    value = excluded.value,
                    importance = excluded.importance,
                    updated_at = excluded.updated_at
                """,
                (
                    memory.key,
                    memory.value,
                    memory.memory_type.value,
                    memory.importance,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )

            row = connection.execute(
                """
                SELECT
                    id,
                    key,
                    value,
                    memory_type,
                    importance,
                    created_at,
                    updated_at
                FROM memories
                WHERE key = ? AND memory_type = ?
                """,
                (
                    memory.key,
                    memory.memory_type.value,
                ),
            ).fetchone()

        if row is None:
            raise RuntimeError(
                "Il ricordo è stato salvato, ma non è stato possibile rileggerlo."
            )

        return self._row_to_memory(row)

    def get_by_id(
        self,
        memory_id: int,
    ) -> Memory | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    key,
                    value,
                    memory_type,
                    importance,
                    created_at,
                    updated_at
                FROM memories
                WHERE id = ?
                """,
                (memory_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_memory(row)

    def get_by_key(
        self,
        key: str,
        memory_type: MemoryType | None = None,
    ) -> list[Memory]:
        clean_key = key.strip()

        if not clean_key:
            return []

        query = """
            SELECT
                id,
                key,
                value,
                memory_type,
                importance,
                created_at,
                updated_at
            FROM memories
            WHERE key = ?
        """

        parameters: list[object] = [clean_key]

        if memory_type is not None:
            query += " AND memory_type = ?"
            parameters.append(memory_type.value)

        query += " ORDER BY importance DESC, updated_at DESC"

        with self._connect() as connection:
            rows = connection.execute(
                query,
                parameters,
            ).fetchall()

        return [
            self._row_to_memory(row)
            for row in rows
        ]

    def get_all(self) -> list[Memory]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    key,
                    value,
                    memory_type,
                    importance,
                    created_at,
                    updated_at
                FROM memories
                ORDER BY importance DESC, updated_at DESC
                """
            ).fetchall()

        return [
            self._row_to_memory(row)
            for row in rows
        ]

    def delete(
        self,
        memory_id: int,
    ) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM memories
                WHERE id = ?
                """,
                (memory_id,),
            )

        return cursor.rowcount > 0

    def clear(self) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM memories"
            )

    def count(self) -> int:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*)
                FROM memories
                """
            ).fetchone()

        return int(row[0]) if row else 0

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    importance INTEGER NOT NULL
                        CHECK(importance BETWEEN 1 AND 10),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(key, memory_type)
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
    def _row_to_memory(
        row: sqlite3.Row,
    ) -> Memory:
        return Memory(
            memory_id=int(row["id"]),
            key=str(row["key"]),
            value=str(row["value"]),
            memory_type=MemoryType(
                str(row["memory_type"])
            ),
            importance=int(row["importance"]),
            created_at=datetime.fromisoformat(
                str(row["created_at"])
            ),
            updated_at=datetime.fromisoformat(
                str(row["updated_at"])
            ),
        )