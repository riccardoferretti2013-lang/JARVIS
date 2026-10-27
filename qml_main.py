import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from src.jarvis.core.assistant import Assistant

from src.jarvis.gui_qml import (
    JarvisBridge,
    QmlTrayIcon,
)

from src.jarvis.gui_qml.vision_bridge import (
    VisionBridge,
)
from src.jarvis.gui_qml.company_bridge import CompanyBridge


def get_runtime_root() -> Path:
    """
    Restituisce la root corretta sia durante
    lo sviluppo Python sia dentro PyInstaller.
    """

    if getattr(
        sys,
        "frozen",
        False,
    ):

        return Path(
            sys._MEIPASS
        )

    return Path(
        __file__
    ).resolve().parent


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

    # ========================================================
    # CORE
    # ========================================================

    assistant = (
        Assistant()
    )

    bridge = (
        JarvisBridge(
            assistant
        )
    )

    company_bridge = CompanyBridge(assistant)

    # ========================================================
    # VISION
    # ========================================================

    vision_bridge = (
        VisionBridge()
    )

    vision_bridge.commandRequested.connect(
        bridge.sendCommand
    )

    # ========================================================
    # QML ENGINE
    # ========================================================

    engine = (
        QQmlApplicationEngine()
    )

    engine.rootContext().setContextProperty(
        "jarvisBridge",
        bridge,
    )

    engine.rootContext().setContextProperty(
        "visionBridge",
        vision_bridge,
    )

    engine.rootContext().setContextProperty(
        "companyBridge",
        company_bridge,
    )

    # ========================================================
    # VISION IMAGE PROVIDER
    # ========================================================

    engine.addImageProvider(
        "vision",
        vision_bridge.image_provider,
    )

    # ========================================================
    # QML FILE
    # ========================================================

    runtime_root = (
        get_runtime_root()
    )

    qml_file = (
        runtime_root
        / "src"
        / "jarvis"
        / "gui_qml"
        / "qml"
        / "Main.qml"
    )

    if not qml_file.exists():

        raise RuntimeError(
            "Main.qml non trovato: "
            f"{qml_file}"
        )

    engine.load(
        QUrl.fromLocalFile(
            str(
                qml_file
            )
        )
    )

    if not engine.rootObjects():

        raise RuntimeError(
            "Impossibile caricare "
            "l'interfaccia QML."
        )

    window = (
        engine.rootObjects()[0]
    )

    # ========================================================
    # SYSTEM TRAY
    # ========================================================

    tray = (
        QmlTrayIcon(
            window=window,
            bridge=bridge,
        )
    )

    tray.show()

    # ========================================================
    # SHUTDOWN
    # ========================================================

    bridge.shutdownFinished.connect(
        vision_bridge.stop
    )

    bridge.shutdownFinished.connect(
        app.quit
    )

    exit_code = (
        app.exec()
    )

    vision_bridge.stop()

    sys.exit(
        exit_code
    )


if __name__ == "__main__":
    main()