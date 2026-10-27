from __future__ import annotations

import json
import threading

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class RequestBudgetStatus:
    date: str
    used: int
    limit: int

    @property
    def remaining(self) -> int:
        return max(
            0,
            self.limit - self.used,
        )

    @property
    def exhausted(self) -> bool:
        return self.remaining <= 0


class DailyRequestBudget:
    """
    Gestisce il limite giornaliero delle chiamate API
    della AI Company di J.A.R.V.I.S.

    Il contatore viene salvato fuori dal repository Git,
    nella cartella:

        C:\\Users\\<utente>\\.jarvis\\api_usage.json

    In questo modo:
    - sopravvive ai riavvii;
    - non viene caricato su GitHub;
    - J.A.R.V.I.S. non supera accidentalmente il limite.
    """

    def __init__(
        self,
        daily_limit: int = 50,
        storage_path: Path | None = None,
    ) -> None:

        if daily_limit < 1:
            raise ValueError(
                "daily_limit deve essere almeno 1."
            )

        self._daily_limit = daily_limit

        self._storage_path = (
            storage_path
            or (
                Path.home()
                / ".jarvis"
                / "api_usage.json"
            )
        )

        self._lock = threading.Lock()

        self._storage_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    @property
    def daily_limit(self) -> int:
        return self._daily_limit

    def get_status(
        self,
    ) -> RequestBudgetStatus:

        with self._lock:

            data = self._load()

            today = self._today()

            if data["date"] != today:

                data = {
                    "date": today,
                    "used": 0,
                }

                self._save(data)

            return RequestBudgetStatus(
                date=today,
                used=data["used"],
                limit=self._daily_limit,
            )

    def can_consume(
        self,
        amount: int = 1,
    ) -> bool:

        if amount < 1:
            return False

        status = self.get_status()

        return (
            status.used + amount
            <= self._daily_limit
        )

    def consume(
        self,
        amount: int = 1,
    ) -> bool:
        """
        Prenota una o più richieste API.

        Incrementiamo PRIMA della chiamata API.

        È intenzionale: se una richiesta fallisce dopo
        essere stata inviata, preferiamo conteggiarla
        comunque per evitare di superare il limite reale.
        """

        if amount < 1:
            return False

        with self._lock:

            data = self._load()

            today = self._today()

            if data["date"] != today:

                data = {
                    "date": today,
                    "used": 0,
                }

            new_total = (
                data["used"]
                + amount
            )

            if new_total > self._daily_limit:
                return False

            data["used"] = new_total

            self._save(data)

            return True

    def remaining(
        self,
    ) -> int:

        return (
            self.get_status()
            .remaining
        )

    def _load(
        self,
    ) -> dict:

        if not self._storage_path.exists():

            return {
                "date": self._today(),
                "used": 0,
            }

        try:

            content = (
                self._storage_path
                .read_text(
                    encoding="utf-8"
                )
            )

            data = json.loads(
                content
            )

            return {
                "date": str(
                    data.get(
                        "date",
                        self._today(),
                    )
                ),
                "used": int(
                    data.get(
                        "used",
                        0,
                    )
                ),
            }

        except Exception:

            return {
                "date": self._today(),
                "used": 0,
            }

    def _save(
        self,
        data: dict,
    ) -> None:

        temporary_path = (
            self._storage_path
            .with_suffix(".tmp")
        )

        temporary_path.write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        temporary_path.replace(
            self._storage_path
        )

    @staticmethod
    def _today() -> str:

        return (
            datetime.now()
            .date()
            .isoformat()
        )