import threading
import time
from datetime import datetime
from typing import Callable

from .database import NodeDatabase


ReminderCallback = Callable[
    [dict],
    None,
]


class ReminderService:

    def __init__(
        self,
        database: NodeDatabase,
        check_interval: float = 1.0,
    ) -> None:

        self._database = database

        self._check_interval = (
            check_interval
        )

        self._stop_event = (
            threading.Event()
        )

        self._thread: (
            threading.Thread
            | None
        ) = None

        self._callbacks: list[
            ReminderCallback
        ] = []

    def start(
        self,
    ) -> None:

        if (
            self._thread is not None
            and self._thread.is_alive()
        ):
            return

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._loop,
            name="JarvisReminderService",
            daemon=True,
        )

        self._thread.start()

    def stop(
        self,
    ) -> None:

        self._stop_event.set()

        if self._thread is not None:

            self._thread.join(
                timeout=3.0
            )

    def add_callback(
        self,
        callback: ReminderCallback,
    ) -> None:

        self._callbacks.append(
            callback
        )

    def add_reminder(
        self,
        message: str,
        remind_at: datetime,
    ) -> int:

        clean_message = (
            message.strip()
        )

        if not clean_message:

            raise ValueError(
                "Il messaggio del promemoria "
                "non può essere vuoto."
            )

        now = (
            datetime.now()
            .astimezone()
        )

        target = (
            remind_at
            if remind_at.tzinfo is not None
            else remind_at.astimezone()
        )

        with (
            self._database.connect()
            as connection
        ):

            cursor = connection.execute(
                """
                INSERT INTO reminders (
                    message,
                    remind_at,
                    created_at,
                    completed
                )
                VALUES (?, ?, ?, 0)
                """,
                (
                    clean_message,
                    target.isoformat(),
                    now.isoformat(),
                ),
            )

            connection.commit()

            return int(
                cursor.lastrowid
            )

    def get_pending(
        self,
    ) -> list[dict]:

        with (
            self._database.connect()
            as connection
        ):

            rows = connection.execute(
                """
                SELECT
                    id,
                    message,
                    remind_at,
                    created_at,
                    completed
                FROM reminders
                WHERE completed = 0
                ORDER BY remind_at ASC
                """
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def complete(
        self,
        reminder_id: int,
    ) -> None:

        with (
            self._database.connect()
            as connection
        ):

            connection.execute(
                """
                UPDATE reminders
                SET completed = 1
                WHERE id = ?
                """,
                (
                    reminder_id,
                ),
            )

            connection.commit()

    def _loop(
        self,
    ) -> None:

        while not (
            self._stop_event.is_set()
        ):

            try:

                self._check_reminders()

            except Exception as exc:

                print(
                    "[REMINDER ERROR]",
                    exc,
                )

            self._stop_event.wait(
                self._check_interval
            )

    def _check_reminders(
        self,
    ) -> None:

        now = (
            datetime.now()
            .astimezone()
        )

        reminders = (
            self.get_pending()
        )

        for reminder in reminders:

            target = (
                datetime.fromisoformat(
                    reminder[
                        "remind_at"
                    ]
                )
            )

            if target > now:
                continue

            for callback in (
                self._callbacks
            ):

                try:

                    callback(
                        reminder
                    )

                except Exception as exc:

                    print(
                        "[REMINDER CALLBACK ERROR]",
                        exc,
                    )

            self.complete(
                reminder[
                    "id"
                ]
            )