import subprocess
import threading
import time

import psutil

from PySide6.QtCore import QObject, Signal


class SystemMonitor(QObject):

    telemetryUpdated = Signal(
        float,
        float,
        float,
        float,
        float,
        float,
        str,
    )

    def __init__(
        self,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self._running = threading.Event()
        self._thread: threading.Thread | None = None

        self._previous_bytes = 0
        self._previous_time = time.time()

    def start(
        self,
    ) -> None:

        if (
            self._thread is not None
            and self._thread.is_alive()
        ):
            return

        network = psutil.net_io_counters()

        self._previous_bytes = (
            network.bytes_sent
            + network.bytes_recv
        )

        self._previous_time = time.time()

        self._running.set()

        self._thread = threading.Thread(
            target=self._worker,
            daemon=True,
            name="JarvisSystemMonitor",
        )

        self._thread.start()

    def stop(
        self,
    ) -> None:
        self._running.clear()

    def _worker(
        self,
    ) -> None:

        psutil.cpu_percent(
            interval=None
        )

        while self._running.is_set():

            try:
                cpu = psutil.cpu_percent(
                    interval=0.5
                )

                memory = (
                    psutil
                    .virtual_memory()
                    .percent
                )

                disk = (
                    psutil
                    .disk_usage(
                        "C:\\"
                    )
                    .percent
                )

                network = (
                    psutil
                    .net_io_counters()
                )

                now = time.time()

                total_bytes = (
                    network.bytes_sent
                    + network.bytes_recv
                )

                elapsed = max(
                    now - self._previous_time,
                    0.001,
                )

                delta = max(
                    total_bytes
                    - self._previous_bytes,
                    0,
                )

                network_mbps = (
                    delta
                    * 8
                    / elapsed
                    / 1_000_000
                )

                self._previous_bytes = (
                    total_bytes
                )

                self._previous_time = now

                gpu = self._read_gpu_usage()

                uptime = self._format_uptime(
                    time.time()
                    - psutil.boot_time()
                )

                performance = (
                    100
                    - (
                        cpu * 0.35
                        + memory * 0.30
                        + disk * 0.10
                        + gpu * 0.25
                    )
                )

                performance = max(
                    0,
                    min(
                        performance,
                        100,
                    ),
                )

                self.telemetryUpdated.emit(
                    cpu,
                    memory,
                    disk,
                    network_mbps,
                    gpu,
                    performance,
                    uptime,
                )

            except Exception:
                pass

            time.sleep(
                0.5
            )

    @staticmethod
    def _read_gpu_usage(
    ) -> float:

        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=utilization.gpu",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=2,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW
                    if hasattr(
                        subprocess,
                        "CREATE_NO_WINDOW",
                    )
                    else 0
                ),
            )

            if result.returncode != 0:
                return 0.0

            first_line = (
                result.stdout
                .strip()
                .splitlines()[0]
            )

            return float(
                first_line.strip()
            )

        except (
            Exception,
            IndexError,
            ValueError,
        ):
            return 0.0

    @staticmethod
    def _format_uptime(
        seconds: float,
    ) -> str:

        seconds = int(
            max(
                0,
                seconds,
            )
        )

        days = seconds // 86400

        hours = (
            seconds % 86400
        ) // 3600

        minutes = (
            seconds % 3600
        ) // 60

        if days > 0:
            return (
                f"{days}d "
                f"{hours:02d}h "
                f"{minutes:02d}m"
            )

        return (
            f"{hours:02d}h "
            f"{minutes:02d}m"
        )