from collections.abc import Callable

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


class QmlTrayIcon(QSystemTrayIcon):

    def __init__(
        self,
        window,
        bridge,
    ) -> None:
        super().__init__()

        self._window = window
        self._bridge = bridge

        self._color = "#FFC857"

        self._build_menu()

        self.setIcon(
            self._create_icon(
                self._color
            )
        )

        self.setToolTip(
            "J.A.R.V.I.S. // STARTING"
        )

        self.activated.connect(
            self._activated
        )

        self._bridge.stateChanged.connect(
            self._state_changed
        )

    def _build_menu(
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
            self._bridge.stopResponse
        )

        exit_action = QAction(
            "Esci da J.A.R.V.I.S.",
            self,
        )

        exit_action.triggered.connect(
            self.exit_jarvis
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

        try:
            self._window.raise_()

        except Exception:
            pass

        try:
            self._window.requestActivate()

        except Exception:
            pass

    def _activated(
        self,
        reason,
    ) -> None:

        if reason in {
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        }:
            self.show_window()

    def exit_jarvis(
        self,
    ) -> None:

        self.hide()

        self._bridge.shutdown()

    def _state_changed(
        self,
        state: str,
        color: str,
    ) -> None:

        self._color = color

        self.setIcon(
            self._create_icon(
                color
            )
        )

        self.setToolTip(
            f"J.A.R.V.I.S. // {state}"
        )

    @staticmethod
    def _create_icon(
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

        painter.setPen(
            QPen(
                QColor(
                    accent.red(),
                    accent.green(),
                    accent.blue(),
                    60,
                ),
                9,
            )
        )

        painter.drawEllipse(
            QRectF(
                9,
                9,
                46,
                46,
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
                12,
                12,
                40,
                40,
            )
        )

        painter.drawEllipse(
            QRectF(
                20,
                20,
                24,
                24,
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
                27,
                27,
                10,
                10,
            )
        )

        painter.end()

        return QIcon(
            pixmap
        )