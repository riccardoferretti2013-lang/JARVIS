import sys

from PySide6.QtWidgets import (
    QApplication,
)

from src.jarvis.core.assistant import (
    Assistant,
)
from src.jarvis.gui import (
    MainWindow,
    TrayIcon,
)


def main() -> None:

    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        "J.A.R.V.I.S."
    )

    app.setQuitOnLastWindowClosed(
        False
    )

    assistant = Assistant()

    window = MainWindow(
        assistant
    )

    tray = TrayIcon(
        window
    )

    window.state_changed.connect(
        tray.set_state
    )

    tray.show()

    window.show()

    exit_code = (
        app.exec()
    )

    sys.exit(
        exit_code
    )


if __name__ == "__main__":
    main()