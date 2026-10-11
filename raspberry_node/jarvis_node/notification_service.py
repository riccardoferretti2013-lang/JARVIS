import requests


class NotificationService:

    def __init__(
        self,
        server_url: str,
        topic: str,
    ) -> None:

        self._server_url = (
            server_url
            .strip()
            .rstrip("/")
        )

        self._topic = (
            topic.strip()
        )

    @property
    def enabled(
        self,
    ) -> bool:

        return bool(
            self._server_url
            and self._topic
        )

    def send(
        self,
        message: str,
        title: str = "J.A.R.V.I.S.",
    ) -> bool:

        if not self.enabled:
            return False

        clean_message = (
            message.strip()
        )

        if not clean_message:
            return False

        url = (
            f"{self._server_url}/"
            f"{self._topic}"
        )

        try:

            response = requests.post(
                url,
                data=clean_message.encode(
                    "utf-8"
                ),
                headers={
                    "Title": title,
                    "Priority": "high",
                    "Tags": "robot,alarm_clock",
                },
                timeout=10,
            )

            response.raise_for_status()

            return True

        except requests.RequestException as exc:

            print(
                "[NOTIFICATION ERROR]",
                exc,
            )

            return False