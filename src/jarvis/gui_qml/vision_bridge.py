from __future__ import annotations

import base64
import threading

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)

from PySide6.QtGui import (
    QImage,
)

from PySide6.QtQuick import (
    QQuickImageProvider,
)

from ..computer.gestures import (
    GestureController,
)


class VisionImageProvider(
    QQuickImageProvider
):
    """
    Image provider utilizzato da QML
    per visualizzare il feed live
    di J.A.R.V.I.S. Vision Control.
    """

    def __init__(
        self,
    ) -> None:

        super().__init__(
            QQuickImageProvider.Image
        )

        self._image = (
            QImage()
        )

        self._lock = (
            threading.Lock()
        )

    # ========================================================
    # SET IMAGE
    # ========================================================

    def set_image(
        self,
        image: QImage,
    ) -> None:

        with self._lock:

            self._image = (
                image.copy()
            )

    # ========================================================
    # REQUEST IMAGE
    # ========================================================

    def requestImage(
        self,
        image_id,
        size,
        requested_size,
    ):

        with self._lock:

            image = (
                self._image.copy()
            )

        if image.isNull():

            image = (
                QImage(
                    1280,
                    720,
                    QImage.Format_RGB32,
                )
            )

            image.fill(
                0
            )

        if (
            requested_size.width()
            > 0
            and requested_size.height()
            > 0
        ):

            image = (
                image.scaled(
                    requested_size
                )
            )

        return image


class VisionBridge(QObject):
    """
    Bridge tra GestureController
    e interfaccia QML.

    Gestisce:

    - webcam
    - frame live
    - stato MediaPipe
    - numero mani
    - stato gesture
    - comando riconosciuto
    """

    frameChanged = Signal(
        str
    )

    statusChanged = Signal(
        bool,
        int,
        str,
        str,
    )

    errorOccurred = Signal(
        str
    )

    commandRequested = Signal(
        str
    )

    def __init__(
        self,
    ) -> None:

        super().__init__()

        self._controller = None

        self._thread = None

        self._running = (
            False
        )

        self._frame_revision = (
            0
        )

        self._image_provider = (
            VisionImageProvider()
        )

    # ========================================================
    # IMAGE PROVIDER
    # ========================================================

    @property
    def image_provider(
        self,
    ) -> VisionImageProvider:

        return (
            self._image_provider
        )

    # ========================================================
    # START
    # ========================================================

    @Slot()
    def start(
        self,
    ) -> None:

        if self._running:
            return

        self._running = (
            True
        )

        self._thread = (
            threading.Thread(
                target=self._vision_worker,
                daemon=True,
                name="JarvisVisionControl",
            )
        )

        self._thread.start()

    # ========================================================
    # STOP
    # ========================================================

    @Slot()
    def stop(
        self,
    ) -> None:

        self._running = (
            False
        )

        if (
            self._controller
            is not None
        ):

            try:

                self._controller.stop()

            except Exception:
                pass

    # ========================================================
    # VISION WORKER
    # ========================================================

    def _vision_worker(
        self,
    ) -> None:

        try:

            self._controller = (
                GestureController(
                    frame_callback=(
                        self._frame_callback
                    ),
                    status_callback=(
                        self._status_callback
                    ),
                    command_callback=(
                        self._command_callback
                    ),
                    show_window=False,
                )
            )

            self._controller.run()

        except Exception as error:

            self.errorOccurred.emit(
                str(error)
            )

            self.statusChanged.emit(
                False,
                0,
                "ERROR",
                "NONE",
            )

        finally:

            self._running = (
                False
            )

    # ========================================================
    # FRAME CALLBACK
    # ========================================================

    def _frame_callback(
        self,
        frame_source: str,
    ) -> None:

        if not self._running:
            return

        try:

            prefix = (
                "data:image/jpeg;base64,"
            )

            if not frame_source.startswith(
                prefix
            ):
                return

            encoded_data = (
                frame_source[
                    len(prefix):
                ]
            )

            raw_data = (
                base64.b64decode(
                    encoded_data
                )
            )

            image = (
                QImage.fromData(
                    raw_data,
                    "JPEG",
                )
            )

            if image.isNull():
                return

            self._image_provider.set_image(
                image
            )

            self._frame_revision += (
                1
            )

            source = (
                "image://vision/frame?"
                + str(
                    self._frame_revision
                )
            )

            self.frameChanged.emit(
                source
            )

        except Exception as error:

            print()
            print(
                "Errore Vision frame:"
            )

            print(
                error
            )

            print()

    # ========================================================
    # STATUS CALLBACK
    # ========================================================

    def _status_callback(
        self,
        camera_online: bool,
        hands_count: int,
        gesture: str,
        command: str,
    ) -> None:

        if not self._running:
            return

        self.statusChanged.emit(
            camera_online,
            hands_count,
            gesture,
            command,
        )

    # ========================================================
    # COMMAND CALLBACK
    # ========================================================

    def _command_callback(
        self,
        command: str,
    ) -> None:

        if not command:
            return

        self.commandRequested.emit(
            command
        )