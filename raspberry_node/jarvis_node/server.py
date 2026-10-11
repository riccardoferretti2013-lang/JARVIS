import threading
from datetime import datetime
from pathlib import Path

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
)

from .config import NodeConfig
from .database import NodeDatabase
from .main_client import JarvisMainClient
from .notification_service import NotificationService
from .reminders import ReminderService
from .wake_on_lan import WakeOnLan


class JarvisNodeServer:

    def __init__(
        self,
        root_path: Path,
    ) -> None:

        self._root_path = root_path

        self._config = NodeConfig(
            self._root_path / "config.json"
        )

        self._database = NodeDatabase(
            self._root_path
            / "data"
            / "jarvis_node.db"
        )

        # ==========================================
        # NOTIFICHE
        # ==========================================

        self._notifications = NotificationService(
            server_url=(
                self._config.notification_server
            ),
            topic=(
                self._config.notification_topic
            ),
        )

        # ==========================================
        # J.A.R.V.I.S. MAIN
        # ==========================================

        self._main_client = JarvisMainClient(
            host=self._config.pc_host,
            port=self._config.pc_port,
        )

        # ==========================================
        # PROMEMORIA
        # ==========================================

        self._reminders = ReminderService(
            database=self._database,
            check_interval=(
                self._config.reminder_check_seconds
            ),
        )

        self._reminders.add_callback(
            self._on_reminder
        )

        # ==========================================
        # STATO SETUP
        # ==========================================

        self._setup_lock = threading.Lock()

        self._setup_running = False

        # ==========================================
        # FLASK
        # ==========================================

        template_folder = (
            self._root_path / "templates"
        )

        static_folder = (
            self._root_path / "static"
        )

        self._app = Flask(
            __name__,
            template_folder=str(
                template_folder
            ),
            static_folder=str(
                static_folder
            ),
        )

        self._configure_routes()

    def run(
        self,
    ) -> None:

        print(
            "================================"
        )

        print(
            self._config.node_name
        )

        print(
            "Server in avvio..."
        )

        print(
            f"Porta: {self._config.port}"
        )

        print(
            "J.A.R.V.I.S. Main: "
            f"{self._config.pc_host}:"
            f"{self._config.pc_port}"
        )

        print(
            "Notifiche: "
            + (
                "ATTIVE"
                if (
                    self._config
                    .notifications_enabled
                )
                else "DISATTIVE"
            )
        )

        print(
            "================================"
        )

        self._reminders.start()

        try:

            self._app.run(
                host=self._config.host,
                port=self._config.port,
                debug=False,
                use_reloader=False,
                threaded=True,
            )

        finally:

            self._reminders.stop()

    def _configure_routes(
        self,
    ) -> None:

        # ==========================================
        # HOME
        # ==========================================

        @self._app.get("/")
        def home():

            return render_template(
                "index.html"
            )

        # ==========================================
        # NODE STATUS
        # ==========================================

        @self._app.get(
            "/api/status"
        )
        def status():

            return jsonify(
                {
                    "node":
                        self._config.node_name,

                    "status":
                        "online",

                    "notifications":
                        (
                            self._config
                            .notifications_enabled
                        ),

                    "time":
                        datetime.now()
                        .astimezone()
                        .isoformat(),
                }
            )

        # ==========================================
        # PC STATUS
        # ==========================================

        @self._app.get(
            "/api/pc/status"
        )
        def pc_status():

            ready = (
                self._main_client.is_ready()
            )

            return jsonify(
                {
                    "ok": True,
                    "ready": ready,
                    "setup_running":
                        self._setup_running,
                }
            )

        # ==========================================
        # ACCENDI SETUP
        # ==========================================

        @self._app.post(
            "/api/pc/setup"
        )
        def pc_setup():

            with self._setup_lock:

                if self._setup_running:

                    return jsonify(
                        {
                            "ok": True,
                            "message":
                                "Setup già in corso.",
                        }
                    )

                self._setup_running = True

            thread = threading.Thread(
                target=self._activate_setup,
                daemon=True,
                name="JarvisSetup",
            )

            thread.start()

            return jsonify(
                {
                    "ok": True,
                    "message":
                        "Avvio setup iniziato.",
                }
            )

        # ==========================================
        # COMANDO GENERICO
        # ==========================================

        @self._app.post(
            "/api/pc/command"
        )
        def pc_command():

            data = (
                request.get_json(
                    silent=True
                )
                or {}
            )

            command = str(
                data.get(
                    "command",
                    "",
                )
            ).strip()

            if not command:

                return jsonify(
                    {
                        "ok": False,
                        "error":
                            "Comando mancante.",
                    }
                ), 400

            if not (
                self._main_client.is_ready()
            ):

                return jsonify(
                    {
                        "ok": False,
                        "error":
                            "J.A.R.V.I.S. Main "
                            "non è disponibile.",
                    }
                ), 503

            success = (
                self._main_client
                .send_command(
                    command
                )
            )

            if not success:

                return jsonify(
                    {
                        "ok": False,
                        "error":
                            "Invio comando fallito.",
                    }
                ), 500

            print(
                "[REMOTE COMMAND] "
                f"{command}"
            )

            return jsonify(
                {
                    "ok": True,
                    "command": command,
                    "message":
                        "Comando inviato.",
                }
            )

        # ==========================================
        # WAKE PC
        # ==========================================

        @self._app.post(
            "/api/pc/wake"
        )
        def wake_pc():

            try:

                self._wake_pc()

            except ValueError as exc:

                return jsonify(
                    {
                        "ok": False,
                        "error":
                            str(exc),
                    }
                ), 400

            return jsonify(
                {
                    "ok": True,
                    "message":
                        "Wake-on-LAN inviato.",
                }
            )

        # ==========================================
        # MODALITA LAVORO
        # ==========================================

        @self._app.post(
            "/api/pc/work-mode"
        )
        def work_mode():

            thread = threading.Thread(
                target=(
                    self._activate_work_mode
                ),
                daemon=True,
                name="JarvisWorkMode",
            )

            thread.start()

            return jsonify(
                {
                    "ok": True,
                    "message":
                        "Preparazione postazione "
                        "avviata.",
                }
            )

        # ==========================================
        # PROMEMORIA
        # ==========================================

        @self._app.get(
            "/api/reminders"
        )
        def reminders():

            return jsonify(
                self._reminders
                .get_pending()
            )

        @self._app.post(
            "/api/reminders"
        )
        def add_reminder():

            data = (
                request.get_json(
                    silent=True
                )
                or {}
            )

            message = str(
                data.get(
                    "message",
                    "",
                )
            ).strip()

            remind_at_raw = (
                data.get(
                    "remind_at"
                )
            )

            if (
                not message
                or not remind_at_raw
            ):

                return jsonify(
                    {
                        "ok": False,
                        "error":
                            "message e remind_at "
                            "sono obbligatori.",
                    }
                ), 400

            try:

                remind_at = (
                    datetime.fromisoformat(
                        str(
                            remind_at_raw
                        ).replace(
                            "Z",
                            "+00:00",
                        )
                    )
                )

            except ValueError:

                return jsonify(
                    {
                        "ok": False,
                        "error":
                            "Formato data "
                            "non valido.",
                    }
                ), 400

            reminder_id = (
                self._reminders
                .add_reminder(
                    message=message,
                    remind_at=remind_at,
                )
            )

            return jsonify(
                {
                    "ok": True,
                    "id":
                        reminder_id,
                }
            )

        # ==========================================
        # TEST NOTIFICHE
        # ==========================================

        @self._app.post(
            "/api/notifications/test"
        )
        def test_notification():

            success = (
                self._send_notification(
                    message=(
                        "Sistema notifiche "
                        "J.A.R.V.I.S. operativo."
                    ),
                    title=(
                        "J.A.R.V.I.S. TEST"
                    ),
                )
            )

            if not success:

                return jsonify(
                    {
                        "ok": False,
                        "error":
                            "Invio notifica fallito.",
                    }
                ), 500

            return jsonify(
                {
                    "ok": True,
                    "message":
                        "Notifica inviata.",
                }
            )

    # ==============================================
    # WAKE
    # ==============================================

    def _wake_pc(
        self,
    ) -> None:

        mac_address = (
            self._config.pc_mac_address
        )

        if not mac_address:

            raise ValueError(
                "MAC address del PC "
                "non configurato."
            )

        WakeOnLan.wake(
            mac_address
        )

    # ==============================================
    # ACCENDI SETUP
    # ==============================================

    def _activate_setup(
        self,
    ) -> None:

        try:

            print(
                "[SETUP] Richiesta ricevuta."
            )

            # PC già pronto
            if self._main_client.is_ready():

                print(
                    "[SETUP] "
                    "J.A.R.V.I.S. Main "
                    "già pronto."
                )

                self._send_notification(
                    message="Setup pronto.",
                    title="J.A.R.V.I.S.",
                )

                return

            # PC non pronto
            print(
                "[SETUP] "
                "Invio Wake-on-LAN..."
            )

            try:

                self._wake_pc()

            except Exception as exc:

                print(
                    "[SETUP] "
                    f"Wake fallito: {exc}"
                )

                self._send_notification(
                    message=(
                        "Impossibile avviare "
                        "il computer."
                    ),
                    title="J.A.R.V.I.S.",
                )

                return

            print(
                "[SETUP] "
                "Attendo avvio Windows "
                "e J.A.R.V.I.S. Main..."
            )

            ready = (
                self._main_client
                .wait_until_ready(
                    timeout=(
                        self._config
                        .pc_startup_timeout_seconds
                    ),
                    poll_interval=(
                        self._config
                        .pc_startup_poll_seconds
                    ),
                )
            )

            if not ready:

                print(
                    "[SETUP] Timeout."
                )

                self._send_notification(
                    message=(
                        "Il computer non è "
                        "diventato pronto "
                        "entro il tempo previsto."
                    ),
                    title="J.A.R.V.I.S.",
                )

                return

            print(
                "[SETUP] SETUP PRONTO."
            )

            self._send_notification(
                message="Setup pronto.",
                title="J.A.R.V.I.S.",
            )

        finally:

            with self._setup_lock:

                self._setup_running = False

    # ==============================================
    # MODALITA LAVORO
    # ==============================================

    def _activate_work_mode(
        self,
    ) -> None:

        print(
            "[WORK MODE] Richiesta ricevuta."
        )

        if not (
            self._main_client.is_ready()
        ):

            print(
                "[WORK MODE] "
                "Invio Wake-on-LAN..."
            )

            try:

                self._wake_pc()

            except Exception as exc:

                print(
                    "[WORK MODE] "
                    f"Wake fallito: {exc}"
                )

                return

            ready = (
                self._main_client
                .wait_until_ready(
                    timeout=(
                        self._config
                        .pc_startup_timeout_seconds
                    ),
                    poll_interval=(
                        self._config
                        .pc_startup_poll_seconds
                    ),
                )
            )

            if not ready:

                self._send_notification(
                    message=(
                        "J.A.R.V.I.S. Main "
                        "non disponibile."
                    ),
                    title="J.A.R.V.I.S.",
                )

                return

        success = (
            self._main_client
            .send_command(
                "modalità lavoro"
            )
        )

        if not success:

            self._send_notification(
                message=(
                    "Errore attivazione "
                    "Modalità lavoro."
                ),
                title="J.A.R.V.I.S.",
            )

            return

        self._send_notification(
            message=(
                "Modalità lavoro avviata."
            ),
            title="J.A.R.V.I.S.",
        )

    # ==============================================
    # NOTIFICHE
    # ==============================================

    def _send_notification(
        self,
        message: str,
        title: str,
    ) -> bool:

        if not (
            self._config
            .notifications_enabled
        ):
            return False

        return self._notifications.send(
            message=message,
            title=title,
        )

    # ==============================================
    # PROMEMORIA
    # ==============================================

    def _on_reminder(
        self,
        reminder: dict,
    ) -> None:

        message = str(
            reminder["message"]
        )

        print()
        print(
            "================================"
        )
        print(
            "PROMEMORIA J.A.R.V.I.S."
        )
        print(
            message
        )
        print(
            "================================"
        )
        print()

        if not (
            self._config
            .notifications_enabled
        ):
            return

        success = (
            self._notifications.send(
                message=message,
                title=(
                    "Promemoria J.A.R.V.I.S."
                ),
            )
        )

        if success:

            print(
                "[NOTIFICATION] "
                "Notifica inviata."
            )

        else:

            print(
                "[NOTIFICATION] "
                "Invio fallito."
            )