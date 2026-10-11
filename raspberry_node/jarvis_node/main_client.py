import time

import requests


class JarvisMainClient:

    def __init__(
        self,
        host: str,
        port: int,
        timeout: float = 3.0,
    ) -> None:

        self._host = host.strip()
        self._port = port
        self._timeout = timeout

    @property
    def base_url(
        self,
    ) -> str:

        return (
            f"http://{self._host}:"
            f"{self._port}"
        )

    def is_ready(
        self,
    ) -> bool:

        try:

            response = requests.get(
                f"{self.base_url}/api/status",
                timeout=self._timeout,
            )

            response.raise_for_status()

            data = response.json()

            return bool(
                data.get(
                    "ready",
                    False,
                )
            )

        except (
            requests.RequestException,
            ValueError,
        ):

            return False

    def wait_until_ready(
        self,
        timeout: float,
        poll_interval: float,
    ) -> bool:

        start_time = time.monotonic()

        while (
            time.monotonic()
            - start_time
            < timeout
        ):

            if self.is_ready():
                return True

            time.sleep(
                poll_interval
            )

        return False

    def send_command(
        self,
        command: str,
    ) -> bool:

        clean_command = (
            command.strip()
        )

        if not clean_command:
            return False

        try:

            response = requests.post(
                (
                    f"{self.base_url}"
                    "/api/command"
                ),
                json={
                    "command":
                        clean_command,
                },
                timeout=10,
            )

            response.raise_for_status()

            data = response.json()

            return bool(
                data.get(
                    "ok",
                    False,
                )
            )

        except (
            requests.RequestException,
            ValueError,
        ):

            return False