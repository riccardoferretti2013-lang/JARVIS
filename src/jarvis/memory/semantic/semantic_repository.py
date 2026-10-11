import json
import sqlite3
from pathlib import Path


class SemanticRepository:
    """
    Salva gli embeddings associati ai ricordi.
    """

    DEFAULT_DATABASE_PATH = Path(
        "data/memory/jarvis_semantic.db"
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
        memory_id: int,
        text: str,
        embedding: list[float],
    ) -> None:
        if memory_id < 1:
            raise ValueError(
                "memory_id deve essere maggiore di zero."
            )

        clean_text = text.strip()

        if not clean_text:
            raise ValueError(
                "Il testo semantico non può essere vuoto."
            )

        if not embedding:
            raise ValueError(
                "L'embedding non può essere vuoto."
            )

        serialized_embedding = json.dumps(
            embedding
        )

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO semantic_memories (
                    memory_id,
                    text,
                    embedding
                )
                VALUES (?, ?, ?)
                ON CONFLICT(memory_id)
                DO UPDATE SET
                    text = excluded.text,
                    embedding = excluded.embedding
                """,
                (
                    memory_id,
                    clean_text,
                    serialized_embedding,
                ),
            )

    def get_all(
        self,
    ) -> list[tuple[int, str, list[float]]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    memory_id,
                    text,
                    embedding
                FROM semantic_memories
                ORDER BY memory_id ASC
                """
            ).fetchall()

        results: list[
            tuple[int, str, list[float]]
        ] = []

        for row in rows:
            embedding_data = json.loads(
                str(row["embedding"])
            )

            embedding = [
                float(value)
                for value in embedding_data
            ]

            results.append(
                (
                    int(row["memory_id"]),
                    str(row["text"]),
                    embedding,
                )
            )

        return results

    def exists(
        self,
        memory_id: int,
    ) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM semantic_memories
                WHERE memory_id = ?
                LIMIT 1
                """,
                (memory_id,),
            ).fetchone()

        return row is not None

    def delete(
        self,
        memory_id: int,
    ) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM semantic_memories
                WHERE memory_id = ?
                """,
                (memory_id,),
            )

        return cursor.rowcount > 0

    def clear(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                DELETE FROM semantic_memories
                """
            )

    def count(self) -> int:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*)
                FROM semantic_memories
                """
            ).fetchone()

        return int(row[0]) if row else 0

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS semantic_memories (
                    memory_id INTEGER PRIMARY KEY,
                    text TEXT NOT NULL,
                    embedding TEXT NOT NULL
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self._database_path
        )

        connection.row_factory = sqlite3.Row

        return connection