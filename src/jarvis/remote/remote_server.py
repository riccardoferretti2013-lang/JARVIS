import threading
from collections.abc import Callable

from flask import (
    Flask,
    jsonify,
    request,
)


class RemoteServer:

    def __init__(
        self,
        command_callback: Callable[
            [str],
            None,
        ],
        status_callback: Callable[
            [],
            str,
        ],
        host: str = "0.0.0.0",
        port: int = 8766,
    ) -> None:

        self._command_callback = (
            command_callback
        )

        self._status_callback = (
            status_callback
        )

        self._host = host
        self._port = port

        self._thread: (
            threading.Thread
            | None
        ) = None

        self._app = Flask(
            "jarvis_main_remote"
        )

        self._configure_routes()

    def _configure_routes(
        self,
    ) -> None:

        @self._app.get(
            "/api/status"
        )
        def status():

            try:

                jarvis_status = (
                    self._status_callback()
                )

            except Exception:

                jarvis_status = (
                    "unknown"
                )

            return jsonify(
                {
                    "ok": True,
                    "jarvis":
                        jarvis_status,
                    "ready":
                        jarvis_status
                        == "online",
                }
            )

        @self._app.post(
            "/api/command"
        )
        def command():

            data = (
                request.get_json(
                    silent=True
                )
                or {}
            )

            command_text = str(
                data.get(
                    "command",
                    "",
                )
            ).strip()

            if not command_text:

                return jsonify(
                    {
                        "ok": False,
                        "error":
                            "Comando mancante.",
                    }
                ), 400

            try:

                thread = (
                    threading.Thread(
                        target=(
                            self._command_callback
                        ),
                        args=(
                            command_text,
                        ),
                        daemon=True,
                        name=(
                            "JarvisRemoteCommand"
                        ),
                    )
                )

                thread.start()

            except Exception as exc:

                return jsonify(
                    {
                        "ok": False,
                        "error":
                            str(exc),
                    }
                ), 500

            return jsonify(
                {
                    "ok": True,
                    "command":
                        command_text,
                    "message":
                        "Comando ricevuto "
                        "da J.A.R.V.I.S. Main.",
                }
            )

    def start(
        self,
    ) -> None:

        if (
            self._thread is not None
            and self._thread.is_alive()
        ):
            return

        self._thread = (
            threading.Thread(
                target=self._run,
                daemon=True,
                name=(
                    "JarvisRemoteServer"
                ),
            )
        )

        self._thread.start()

    def _run(
        self,
    ) -> None:

        self._app.run(
            host=self._host,
            port=self._port,
            debug=False,
            use_reloader=False,
            threaded=True,
        )