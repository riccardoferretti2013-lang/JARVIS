import sqlite3
from pathlib import Path


class NodeDatabase:

    def __init__(
        self,
        database_path: Path,
    ) -> None:

        self._database_path = (
            database_path
        )

        self._database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.initialize()

    def connect(
        self,
    ) -> sqlite3.Connection:

        connection = sqlite3.connect(
            self._database_path,
            check_same_thread=False,
        )

        connection.row_factory = (
            sqlite3.Row
        )

        return connection

    def initialize(
        self,
    ) -> None:

        with self.connect() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    remind_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0
                )
                """
            )

            connection.commit()