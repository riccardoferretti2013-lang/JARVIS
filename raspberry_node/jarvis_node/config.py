import json
from pathlib import Path
from typing import Any


class NodeConfig:

    def __init__(
        self,
        config_path: Path,
    ) -> None:

        self._config_path = config_path
        self._data: dict[str, Any] = {}

        self.load()

    def load(
        self,
    ) -> None:

        if not self._config_path.exists():

            raise FileNotFoundError(
                "Configurazione non trovata: "
                f"{self._config_path}"
            )

        with self._config_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            self._data = json.load(
                file
            )

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self._data.get(
            key,
            default,
        )

    def _pc(
        self,
    ) -> dict:

        return self._data.get(
            "pc",
            {},
        )

    def _notifications(
        self,
    ) -> dict:

        return self._data.get(
            "notifications",
            {},
        )

    @property
    def node_name(
        self,
    ) -> str:

        return str(
            self._data.get(
                "node_name",
                "J.A.R.V.I.S. Node",
            )
        )

    @property
    def host(
        self,
    ) -> str:

        return str(
            self._data.get(
                "host",
                "0.0.0.0",
            )
        )

    @property
    def port(
        self,
    ) -> int:

        return int(
            self._data.get(
                "port",
                8765,
            )
        )

    @property
    def reminder_check_seconds(
        self,
    ) -> float:

        return float(
            self._data.get(
                "reminder_check_seconds",
                1,
            )
        )

    @property
    def pc_name(
        self,
    ) -> str:

        return str(
            self._pc().get(
                "name",
                "J.A.R.V.I.S. Main",
            )
        )

    @property
    def pc_host(
        self,
    ) -> str:

        return str(
            self._pc().get(
                "host",
                "127.0.0.1",
            )
        )

    @property
    def pc_port(
        self,
    ) -> int:

        return int(
            self._pc().get(
                "port",
                8766,
            )
        )

    @property
    def pc_mac_address(
        self,
    ) -> str:

        return str(
            self._pc().get(
                "mac_address",
                "",
            )
        )

    @property
    def pc_startup_timeout_seconds(
        self,
    ) -> float:

        return float(
            self._pc().get(
                "startup_timeout_seconds",
                120,
            )
        )

    @property
    def pc_startup_poll_seconds(
        self,
    ) -> float:

        return float(
            self._pc().get(
                "startup_poll_seconds",
                2,
            )
        )

    @property
    def notifications_enabled(
        self,
    ) -> bool:

        return bool(
            self._notifications().get(
                "enabled",
                False,
            )
        )

    @property
    def notification_server(
        self,
    ) -> str:

        return str(
            self._notifications().get(
                "server",
                "",
            )
        ).rstrip("/")

    @property
    def notification_topic(
        self,
    ) -> str:

        return str(
            self._notifications().get(
                "topic",
                "",
            )
        ).strip()