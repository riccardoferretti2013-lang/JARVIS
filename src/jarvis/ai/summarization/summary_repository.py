import sqlite3
from datetime import datetime
from pathlib import Path

from .conversation_summary import ConversationSummary


class SummaryRepository:
    """
    Salva permanentemente il riassunto
    della conversazione.
    """

    DEFAULT_DATABASE_PATH = Path(
        "data/summaries/jarvis_summaries.db"
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
        summary: ConversationSummary,
    ) -> ConversationSummary:
        now = datetime.now().isoformat()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO conversation_summary (
                    id,
                    content,
                    summarized_messages,
                    created_at,
                    updated_at
                )
                VALUES (1, ?, ?, ?, ?)
                ON CONFLICT(id)
                DO UPDATE SET
                    content = excluded.content,
                    summarized_messages = excluded.summarized_messages,
                    updated_at = excluded.updated_at
                """,
                (
                    summary.content,
                    summary.summarized_messages,
                    now,
                    now,
                ),
            )

        saved_summary = self.get()

        if saved_summary is None:
            raise RuntimeError(
                "Impossibile rileggere il riassunto salvato."
            )

        return saved_summary

    def get(
        self,
    ) -> ConversationSummary | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    content,
                    summarized_messages,
                    created_at,
                    updated_at
                FROM conversation_summary
                WHERE id = 1
                """
            ).fetchone()

        if row is None:
            return None

        return ConversationSummary(
            summary_id=int(row["id"]),
            content=str(row["content"]),
            summarized_messages=int(
                row["summarized_messages"]
            ),
            created_at=datetime.fromisoformat(
                str(row["created_at"])
            ),
            updated_at=datetime.fromisoformat(
                str(row["updated_at"])
            ),
        )

    def clear(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                DELETE FROM conversation_summary
                """
            )

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_summary (
                    id INTEGER PRIMARY KEY CHECK(id = 1),
                    content TEXT NOT NULL,
                    summarized_messages INTEGER NOT NULL,
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