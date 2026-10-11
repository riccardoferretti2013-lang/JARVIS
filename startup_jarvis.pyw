import socket
import subprocess
import time

from qml_main import main


OLLAMA_HOST = "127.0.0.1"
OLLAMA_PORT = 11434

OLLAMA_START_TIMEOUT = 15


def ollama_is_running() -> bool:
    try:
        with socket.create_connection(
            (
                OLLAMA_HOST,
                OLLAMA_PORT,
            ),
            timeout=1,
        ):
            return True

    except OSError:
        return False


def start_ollama() -> None:
    if ollama_is_running():
        return

    creation_flags = 0

    if hasattr(
        subprocess,
        "CREATE_NO_WINDOW",
    ):
        creation_flags = (
            subprocess.CREATE_NO_WINDOW
        )

    try:
        subprocess.Popen(
            [
                "ollama",
                "serve",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creation_flags,
        )

    except Exception:
        return

    deadline = (
        time.time()
        + OLLAMA_START_TIMEOUT
    )

    while time.time() < deadline:

        if ollama_is_running():
            return

        time.sleep(
            0.5
        )


def startup() -> None:
    start_ollama()

    main()


if __name__ == "__main__":
    startup()