import math

from PySide6.QtCore import (
    QPointF,
    QRectF,
    Qt,
    QTimer,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class FuturisticBackground(QWidget):
    """
    Sfondo tecnico/cinematografico.
    """

    def __init__(
        self,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self._scan = 0

        self._timer = QTimer(
            self
        )

        self._timer.timeout.connect(
            self._animate
        )

        self._timer.start(
            45
        )

    def _animate(
        self,
    ) -> None:
        self._scan += 2

        if self._scan > self.height():
            self._scan = 0

        self.update()

    def paintEvent(
        self,
        event,
    ) -> None:
        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        width = self.width()
        height = self.height()

        # Sfondo
        gradient = QLinearGradient(
            0,
            0,
            width,
            height,
        )

        gradient.setColorAt(
            0.0,
            QColor("#01050A"),
        )

        gradient.setColorAt(
            0.45,
            QColor("#020A12"),
        )

        gradient.setColorAt(
            1.0,
            QColor("#000307"),
        )

        painter.fillRect(
            self.rect(),
            gradient,
        )

        # Glow centrale molto delicato
        radial = QRadialGradient(
            QPointF(
                width * 0.58,
                height * 0.45,
            ),
            width * 0.55,
        )

        radial.setColorAt(
            0.0,
            QColor(
                0,
                125,
                210,
                32,
            ),
        )

        radial.setColorAt(
            0.55,
            QColor(
                0,
                60,
                120,
                10,
            ),
        )

        radial.setColorAt(
            1.0,
            QColor(
                0,
                0,
                0,
                0,
            ),
        )

        painter.fillRect(
            self.rect(),
            radial,
        )

        # Griglia tecnica
        grid_pen = QPen(
            QColor(
                40,
                110,
                150,
                18,
            )
        )

        grid_pen.setWidth(
            1
        )

        painter.setPen(
            grid_pen
        )

        spacing = 38

        for x in range(
            0,
            width,
            spacing,
        ):
            painter.drawLine(
                x,
                0,
                x,
                height,
            )

        for y in range(
            0,
            height,
            spacing,
        ):
            painter.drawLine(
                0,
                y,
                width,
                y,
            )

        # Linee secondarie
        fine_pen = QPen(
            QColor(
                20,
                85,
                120,
                10,
            )
        )

        painter.setPen(
            fine_pen
        )

        for x in range(
            0,
            width,
            10,
        ):
            painter.drawLine(
                x,
                0,
                x,
                height,
            )

        # Scanline
        scan_gradient = QLinearGradient(
            0,
            self._scan - 45,
            0,
            self._scan + 45,
        )

        scan_gradient.setColorAt(
            0.0,
            QColor(
                0,
                180,
                255,
                0,
            ),
        )

        scan_gradient.setColorAt(
            0.5,
            QColor(
                0,
                180,
                255,
                15,
            ),
        )

        scan_gradient.setColorAt(
            1.0,
            QColor(
                0,
                180,
                255,
                0,
            ),
        )

        painter.fillRect(
            QRectF(
                0,
                self._scan - 45,
                width,
                90,
            ),
            scan_gradient,
        )

        # Vignettatura
        vignette = QRadialGradient(
            QPointF(
                width / 2,
                height / 2,
            ),
            max(
                width,
                height,
            ) * 0.75,
        )

        vignette.setColorAt(
            0.4,
            QColor(
                0,
                0,
                0,
                0,
            ),
        )

        vignette.setColorAt(
            1.0,
            QColor(
                0,
                0,
                0,
                150,
            ),
        )

        painter.fillRect(
            self.rect(),
            vignette,
        )


class JarvisOrb(QWidget):
    """
    Core HUD avanzato di J.A.R.V.I.S.
    """

    def __init__(
        self,
        parent=None,
    ) -> None:
        super().__init__(
            parent
        )

        self._angle = 0.0
        self._secondary_angle = 0.0
        self._pulse = 0.0
        self._pulse_direction = 1
        self._activity = 0.25

        self.setMinimumSize(
            300,
            300,
        )

        self._timer = QTimer(
            self
        )

        self._timer.timeout.connect(
            self._animate
        )

        self._timer.start(
            30
        )

    def set_activity(
        self,
        value: float,
    ) -> None:
        self._activity = max(
            0.1,
            min(
                value,
                2.0,
            ),
        )

    def _animate(
        self,
    ) -> None:
        self._angle += (
            0.75
            * self._activity
        )

        self._secondary_angle -= (
            0.38
            * self._activity
        )

        self._pulse += (
            0.018
            * self._pulse_direction
            * self._activity
        )

        if self._pulse >= 1.0:
            self._pulse_direction = -1

        elif self._pulse <= 0.0:
            self._pulse_direction = 1

        self.update()

    def paintEvent(
        self,
        event,
    ) -> None:
        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        width = self.width()
        height = self.height()

        size = min(
            width,
            height,
        )

        painter.translate(
            width / 2,
            height / 2,
        )

        cyan = QColor(
            "#00D9FF"
        )

        blue = QColor(
            "#087CC1"
        )

        white = QColor(
            "#EAFBFF"
        )

        # Glow
        glow = QRadialGradient(
            QPointF(
                0,
                0,
            ),
            size * 0.42,
        )

        glow.setColorAt(
            0.0,
            QColor(
                0,
                180,
                255,
                45,
            ),
        )

        glow.setColorAt(
            0.35,
            QColor(
                0,
                110,
                200,
                20,
            ),
        )

        glow.setColorAt(
            1.0,
            QColor(
                0,
                0,
                0,
                0,
            ),
        )

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            glow
        )

        painter.drawEllipse(
            QRectF(
                -size * 0.43,
                -size * 0.43,
                size * 0.86,
                size * 0.86,
            )
        )

        # Cerchi sottili
        for ratio, alpha, width_pen in [
            (0.90, 35, 1),
            (0.78, 80, 1),
            (0.64, 125, 2),
            (0.48, 85, 1),
        ]:

            painter.setPen(
                QPen(
                    QColor(
                        0,
                        195,
                        255,
                        alpha,
                    ),
                    width_pen,
                )
            )

            diameter = (
                size * ratio
            )

            painter.drawEllipse(
                QRectF(
                    -diameter / 2,
                    -diameter / 2,
                    diameter,
                    diameter,
                )
            )

        # Tacche esterne
        painter.save()

        painter.rotate(
            self._angle
        )

        radius_start = (
            size * 0.39
        )

        radius_end = (
            size * 0.425
        )

        for degree in range(
            0,
            360,
            6,
        ):

            rad = math.radians(
                degree
            )

            if degree % 30 == 0:
                alpha = 210
                thickness = 2
            else:
                alpha = 55
                thickness = 1

            painter.setPen(
                QPen(
                    QColor(
                        0,
                        210,
                        255,
                        alpha,
                    ),
                    thickness,
                )
            )

            painter.drawLine(
                QPointF(
                    math.cos(rad)
                    * radius_start,
                    math.sin(rad)
                    * radius_start,
                ),
                QPointF(
                    math.cos(rad)
                    * radius_end,
                    math.sin(rad)
                    * radius_end,
                ),
            )

        painter.restore()

        # Archi principali
        painter.save()

        painter.rotate(
            self._angle
        )

        arc_rect = QRectF(
            -size * 0.36,
            -size * 0.36,
            size * 0.72,
            size * 0.72,
        )

        painter.setPen(
            QPen(
                cyan,
                3,
            )
        )

        for start, span in [
            (14, 42),
            (91, 22),
            (165, 55),
            (254, 30),
            (310, 25),
        ]:
            painter.drawArc(
                arc_rect,
                start * 16,
                span * 16,
            )

        painter.restore()

        # Anello secondario
        painter.save()

        painter.rotate(
            self._secondary_angle
        )

        second_rect = QRectF(
            -size * 0.29,
            -size * 0.29,
            size * 0.58,
            size * 0.58,
        )

        painter.setPen(
            QPen(
                blue,
                2,
            )
        )

        for start, span in [
            (5, 65),
            (110, 30),
            (190, 75),
            (300, 35),
        ]:
            painter.drawArc(
                second_rect,
                start * 16,
                span * 16,
            )

        painter.restore()

        # Croce centrale tecnica
        painter.setPen(
            QPen(
                QColor(
                    0,
                    190,
                    255,
                    45,
                ),
                1,
            )
        )

        painter.drawLine(
            QPointF(
                -size * 0.21,
                0,
            ),
            QPointF(
                size * 0.21,
                0,
            ),
        )

        painter.drawLine(
            QPointF(
                0,
                -size * 0.21,
            ),
            QPointF(
                0,
                size * 0.21,
            ),
        )

        # Nucleo
        core_radius = (
            size
            * (
                0.082
                + self._pulse * 0.006
            )
        )

        core_gradient = QRadialGradient(
            QPointF(
                0,
                0,
            ),
            core_radius,
        )

        core_gradient.setColorAt(
            0.0,
            QColor(
                230,
                252,
                255,
                245,
            ),
        )

        core_gradient.setColorAt(
            0.18,
            QColor(
                0,
                225,
                255,
                235,
            ),
        )

        core_gradient.setColorAt(
            0.58,
            QColor(
                0,
                100,
                185,
                160,
            ),
        )

        core_gradient.setColorAt(
            1.0,
            QColor(
                0,
                40,
                80,
                20,
            ),
        )

        painter.setBrush(
            core_gradient
        )

        painter.setPen(
            QPen(
                white,
                1,
            )
        )

        painter.drawEllipse(
            QRectF(
                -core_radius,
                -core_radius,
                core_radius * 2,
                core_radius * 2,
            )
        )

        # Punto centrale
        painter.setBrush(
            white
        )

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.drawEllipse(
            QRectF(
                -3,
                -3,
                6,
                6,
            )
        )


class InfoCard(QFrame):

    def __init__(
        self,
        title: str,
        value: str = "",
        parent=None,
    ) -> None:
        super().__init__(
            parent
        )

        self.setObjectName(
            "infoCard"
        )

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            15,
            12,
            15,
            12,
        )

        layout.setSpacing(
            7
        )

        self.title_label = QLabel(
            title
        )

        self.title_label.setObjectName(
            "cardTitle"
        )

        self.value_label = QLabel(
            value
        )

        self.value_label.setObjectName(
            "cardValue"
        )

        self.value_label.setWordWrap(
            True
        )

        layout.addWidget(
            self.title_label
        )

        layout.addWidget(
            self.value_label
        )

    def set_value(
        self,
        value: str,
    ) -> None:
        self.value_label.setText(
            value
        )