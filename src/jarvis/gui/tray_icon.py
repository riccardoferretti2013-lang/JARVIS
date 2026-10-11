from PySide6.QtCore import (
    QRectF,
)
from PySide6.QtGui import (
    QAction,
    QColor,
    QIcon,
    QPainter,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QMenu,
    QSystemTrayIcon,
)

from .status_manager import (
    JarvisState,
    StatusManager,
)


class TrayIcon(QSystemTrayIcon):

    def __init__(
        self,
        window,
    ) -> None:

        super().__init__()

        self._window = window

        self._create_menu()

        self.activated.connect(
            self._handle_activation
        )

        self.set_state(
            JarvisState.STARTING
        )

    def _create_menu(
        self,
    ) -> None:

        menu = QMenu()

        open_action = QAction(
            "Apri J.A.R.V.I.S.",
            self,
        )

        open_action.triggered.connect(
            self.show_window
        )

        stop_action = QAction(
            "Interrompi risposta",
            self,
        )

        stop_action.triggered.connect(
            self._stop_response
        )

        exit_action = QAction(
            "Esci da J.A.R.V.I.S.",
            self,
        )

        exit_action.triggered.connect(
            self._exit_jarvis
        )

        menu.addAction(
            open_action
        )

        menu.addAction(
            stop_action
        )

        menu.addSeparator()

        menu.addAction(
            exit_action
        )

        self.setContextMenu(
            menu
        )

    def show_window(
        self,
    ) -> None:

        self._window.show()

        self._window.showNormal()

        self._window.raise_()

        self._window.activateWindow()

    def _stop_response(
        self,
    ) -> None:

        self._window._stop_response()

    def _handle_activation(
        self,
        reason,
    ) -> None:

        if reason in {
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        }:
            self.show_window()

    def _exit_jarvis(
        self,
    ) -> None:

        self.hide()

        self._window.shutdown_and_close()

        app = QApplication.instance()

        if app is not None:
            app.quit()

    def set_state(
        self,
        state: JarvisState,
    ) -> None:

        color = (
            StatusManager.color(
                state
            )
        )

        label = (
            StatusManager.label(
                state
            )
        )

        self.setIcon(
            self._create_jarvis_icon(
                color
            )
        )

        self.setToolTip(
            f"J.A.R.V.I.S.\n{label}"
        )

    @staticmethod
    def _create_jarvis_icon(
        color: str,
    ) -> QIcon:

        pixmap = QPixmap(
            64,
            64,
        )

        pixmap.fill(
            QColor(
                "transparent"
            )
        )

        painter = QPainter(
            pixmap
        )

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        accent = QColor(
            color
        )

        glow = QColor(
            accent
        )

        glow.setAlpha(
            55
        )

        painter.setPen(
            QPen(
                glow,
                9,
            )
        )

        painter.drawEllipse(
            QRectF(
                10,
                10,
                44,
                44,
            )
        )

        painter.setPen(
            QPen(
                accent,
                3,
            )
        )

        painter.drawEllipse(
            QRectF(
                11,
                11,
                42,
                42,
            )
        )

        painter.setPen(
            QPen(
                QColor(
                    "#DDF8FF"
                ),
                2,
            )
        )

        painter.drawEllipse(
            QRectF(
                19,
                19,
                26,
                26,
            )
        )

        painter.setBrush(
            accent
        )

        painter.setPen(
            QPen(
                accent,
                1,
            )
        )

        painter.drawEllipse(
            QRectF(
                26,
                26,
                12,
                12,
            )
        )

        painter.end()

        return QIcon(
            pixmap
        )