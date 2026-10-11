from __future__ import annotations

import base64
import json
import math
import threading
import time

from pathlib import Path
from typing import Callable
from urllib.error import (
    HTTPError,
    URLError,
)
from urllib.request import (
    Request,
    urlopen,
    urlretrieve,
)

import cv2
import mediapipe as mp


# ============================================================
# CAMERA
# ============================================================

CAMERA_INDEX = 0

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720


# ============================================================
# GUI VIDEO
# ============================================================

GUI_FRAME_INTERVAL = 1.0 / 15.0

GUI_JPEG_QUALITY = 75


# ============================================================
# J.A.R.V.I.S. LOCAL API
#
# Usata solo quando GestureController viene eseguito
# autonomamente, senza VisionBridge.
# ============================================================

JARVIS_API_URL = (
    "http://127.0.0.1:8766/api/command"
)

JARVIS_API_TIMEOUT = 2.0


# ============================================================
# CLAP SETTINGS
# ============================================================

CLAP_READY_DISTANCE = 0.22

CLAP_CENTER_CLOSE_DISTANCE = 0.17

CLAP_MIN_POINT_DISTANCE = 0.055

CLAP_RELEASE_DISTANCE = 0.21

CLAP_RELEASE_TIMEOUT = 0.80

CLAP_APPROACH_TIMEOUT = 1.50

CLAP_COOLDOWN = 1.0


# ============================================================
# MEDIAPIPE MODEL
# ============================================================

MODEL_URL = (
    "https://storage.googleapis.com/"
    "mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/latest/"
    "hand_landmarker.task"
)

MODEL_PATH = (
    Path(__file__).resolve().parent
    / "hand_landmarker.task"
)


FrameCallback = Callable[
    [str],
    None,
]

StatusCallback = Callable[
    [
        bool,
        int,
        str,
        str,
    ],
    None,
]

CommandCallback = Callable[
    [str],
    None,
]


class GestureController:
    """
    J.A.R.V.I.S. Vision Control V5.

    Può funzionare in due modalità:

    1. Integrata nella GUI:
       - nessuna finestra OpenCV
       - frame inviati a QML
       - comandi inviati tramite callback

    2. Standalone:
       - finestra OpenCV
       - comando inviato alla Remote API locale
    """

    def __init__(
        self,
        frame_callback: FrameCallback | None = None,
        status_callback: StatusCallback | None = None,
        command_callback: CommandCallback | None = None,
        show_window: bool = True,
    ) -> None:

        self._frame_callback = (
            frame_callback
        )

        self._status_callback = (
            status_callback
        )

        self._command_callback = (
            command_callback
        )

        self._show_window = (
            show_window
        )

        self._stop_event = (
            threading.Event()
        )

        self._camera_online = (
            False
        )

        self._hands_count = (
            0
        )

        self._clap_stage = (
            "WAIT_OPEN"
        )

        self._ready_started_at = (
            0.0
        )

        self._contact_started_at = (
            0.0
        )

        self._last_clap_time = (
            0.0
        )

        self._last_gesture = (
            "WAITING"
        )

        self._last_command = (
            "NONE"
        )

        self._command_message = (
            ""
        )

        self._command_message_until = (
            0.0
        )

        self._center_distance = (
            0.0
        )

        self._minimum_distance = (
            0.0
        )

        self._jarvis_status = (
            "UNKNOWN"
        )

        self._last_gui_frame_time = (
            0.0
        )

        self._last_status_emit_time = (
            0.0
        )

        self._last_emitted_status = (
            None
        )

        self._ensure_model()

        BaseOptions = (
            mp.tasks.BaseOptions
        )

        HandLandmarker = (
            mp.tasks.vision.HandLandmarker
        )

        HandLandmarkerOptions = (
            mp.tasks.vision.HandLandmarkerOptions
        )

        RunningMode = (
            mp.tasks.vision.RunningMode
        )

        options = (
            HandLandmarkerOptions(
                base_options=BaseOptions(
                    model_asset_path=str(
                        MODEL_PATH
                    )
                ),
                running_mode=(
                    RunningMode.VIDEO
                ),
                num_hands=2,
                min_hand_detection_confidence=0.60,
                min_hand_presence_confidence=0.60,
                min_tracking_confidence=0.60,
            )
        )

        self._detector = (
            HandLandmarker
            .create_from_options(
                options
            )
        )

    # ========================================================
    # MODEL
    # ========================================================

    @staticmethod
    def _ensure_model() -> None:

        if MODEL_PATH.exists():
            return

        MODEL_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        print(
            "Download modello MediaPipe..."
        )

        urlretrieve(
            MODEL_URL,
            MODEL_PATH,
        )

        print(
            "Modello MediaPipe scaricato."
        )

    # ========================================================
    # STOP
    # ========================================================

    def stop(
        self,
    ) -> None:

        self._stop_event.set()

    # ========================================================
    # RUN
    # ========================================================

    def run(
        self,
    ) -> None:

        self._stop_event.clear()

        camera = (
            cv2.VideoCapture(
                CAMERA_INDEX
            )
        )

        camera.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            FRAME_WIDTH,
        )

        camera.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            FRAME_HEIGHT,
        )

        if not camera.isOpened():

            self._camera_online = (
                False
            )

            self._last_gesture = (
                "CAMERA ERROR"
            )

            self._emit_status(
                force=True
            )

            raise RuntimeError(
                "Impossibile aprire la webcam."
            )

        self._camera_online = (
            True
        )

        self._last_gesture = (
            "WAITING"
        )

        self._emit_status(
            force=True
        )

        print()
        print(
            "J.A.R.V.I.S. VISION CONTROL V5"
        )
        print()

        if self._show_window:

            print(
                "Modalita: STANDALONE"
            )

        else:

            print(
                "Modalita: GUI INTEGRATED"
            )

        print(
            "Applauso = Modalita lavoro"
        )

        print(
            "Cooldown = 1 secondo"
        )

        if self._show_window:

            print(
                "Q = uscita"
            )

        print()

        start_time = (
            time.monotonic()
        )

        try:

            while (
                not self._stop_event.is_set()
            ):

                ok, frame = (
                    camera.read()
                )

                if not ok:

                    self._camera_online = (
                        False
                    )

                    self._last_gesture = (
                        "CAMERA SIGNAL LOST"
                    )

                    self._emit_status()

                    time.sleep(
                        0.02
                    )

                    continue

                self._camera_online = (
                    True
                )

                frame = (
                    cv2.flip(
                        frame,
                        1,
                    )
                )

                rgb_frame = (
                    cv2.cvtColor(
                        frame,
                        cv2.COLOR_BGR2RGB,
                    )
                )

                mp_image = (
                    mp.Image(
                        image_format=(
                            mp.ImageFormat.SRGB
                        ),
                        data=rgb_frame,
                    )
                )

                timestamp_ms = int(
                    (
                        time.monotonic()
                        - start_time
                    )
                    * 1000
                )

                result = (
                    self._detector
                    .detect_for_video(
                        mp_image,
                        timestamp_ms,
                    )
                )

                hands = (
                    result.hand_landmarks
                    if result.hand_landmarks
                    else []
                )

                self._hands_count = (
                    len(hands)
                )

                for hand in hands:

                    self._draw_hand(
                        frame,
                        hand,
                    )

                self._process_gestures(
                    hands
                )

                self._draw_interface(
                    frame,
                    len(hands),
                )

                self._emit_status()

                self._emit_frame(
                    frame
                )

                if self._show_window:

                    cv2.imshow(
                        (
                            "J.A.R.V.I.S. "
                            "Vision Control V5"
                        ),
                        frame,
                    )

                    key = (
                        cv2.waitKey(1)
                        & 0xFF
                    )

                    if key == ord("q"):

                        self.stop()

                        break

        finally:

            self._camera_online = (
                False
            )

            self._hands_count = (
                0
            )

            self._last_gesture = (
                "OFFLINE"
            )

            self._emit_status(
                force=True
            )

            camera.release()

            try:

                self._detector.close()

            except Exception:
                pass

            if self._show_window:

                cv2.destroyAllWindows()

            print(
                "J.A.R.V.I.S. Vision Control arrestato."
            )

    # ========================================================
    # FRAME → QML
    # ========================================================

    def _emit_frame(
        self,
        frame,
    ) -> None:

        if (
            self._frame_callback
            is None
        ):

            return

        now = (
            time.monotonic()
        )

        if (
            now
            - self._last_gui_frame_time
            < GUI_FRAME_INTERVAL
        ):

            return

        self._last_gui_frame_time = (
            now
        )

        encode_parameters = [
            int(
                cv2.IMWRITE_JPEG_QUALITY
            ),
            GUI_JPEG_QUALITY,
        ]

        success, encoded = (
            cv2.imencode(
                ".jpg",
                frame,
                encode_parameters,
            )
        )

        if not success:
            return

        image_base64 = (
            base64.b64encode(
                encoded.tobytes()
            )
            .decode(
                "ascii"
            )
        )

        source = (
            "data:image/jpeg;base64,"
            + image_base64
        )

        try:

            self._frame_callback(
                source
            )

        except Exception as error:

            print(
                "Errore frame callback:"
            )

            print(
                error
            )

    # ========================================================
    # STATUS → QML
    # ========================================================

    def _emit_status(
        self,
        force: bool = False,
    ) -> None:

        if (
            self._status_callback
            is None
        ):

            return

        status = (
            self._camera_online,
            self._hands_count,
            self._last_gesture,
            self._last_command,
        )

        now = (
            time.monotonic()
        )

        changed = (
            status
            != self._last_emitted_status
        )

        refresh_due = (
            now
            - self._last_status_emit_time
            >= 0.25
        )

        if (
            not force
            and not changed
            and not refresh_due
        ):

            return

        self._last_emitted_status = (
            status
        )

        self._last_status_emit_time = (
            now
        )

        try:

            self._status_callback(
                self._camera_online,
                self._hands_count,
                self._last_gesture,
                self._last_command,
            )

        except Exception as error:

            print(
                "Errore status callback:"
            )

            print(
                error
            )

    # ========================================================
    # GESTURE PROCESSING
    # ========================================================

    def _process_gestures(
        self,
        hands,
    ) -> None:

        if len(hands) < 2:

            self._center_distance = (
                0.0
            )

            self._minimum_distance = (
                0.0
            )

            self._last_gesture = (
                "WAITING FOR 2 HANDS"
            )

            self._reset_clap()

            return

        first_hand = (
            hands[0]
        )

        second_hand = (
            hands[1]
        )

        first_center = (
            self._hand_center(
                first_hand
            )
        )

        second_center = (
            self._hand_center(
                second_hand
            )
        )

        self._center_distance = (
            self._point_distance(
                first_center,
                second_center,
            )
        )

        self._minimum_distance = (
            self._minimum_hand_distance(
                first_hand,
                second_hand,
            )
        )

        self._process_clap()

    # ========================================================
    # CLAP STATE MACHINE
    # ========================================================

    def _process_clap(
        self,
    ) -> None:

        now = (
            time.monotonic()
        )

        # ----------------------------------------------------
        # COOLDOWN
        # ----------------------------------------------------

        if (
            now
            - self._last_clap_time
            < CLAP_COOLDOWN
        ):

            self._last_gesture = (
                "COOLDOWN"
            )

            return

        # ----------------------------------------------------
        # WAIT OPEN
        # ----------------------------------------------------

        if (
            self._clap_stage
            == "WAIT_OPEN"
        ):

            self._last_gesture = (
                "OPEN HANDS"
            )

            if (
                self._center_distance
                >= CLAP_READY_DISTANCE
            ):

                self._clap_stage = (
                    "READY"
                )

                self._ready_started_at = (
                    now
                )

                self._last_gesture = (
                    "READY"
                )

            return

        # ----------------------------------------------------
        # READY
        # ----------------------------------------------------

        if (
            self._clap_stage
            == "READY"
        ):

            self._last_gesture = (
                "READY"
            )

            ready_elapsed = (
                now
                - self._ready_started_at
            )

            if (
                ready_elapsed
                > CLAP_APPROACH_TIMEOUT
            ):

                self._reset_clap()

                return

            hands_close = (
                self._center_distance
                <= CLAP_CENTER_CLOSE_DISTANCE
            )

            points_close = (
                self._minimum_distance
                <= CLAP_MIN_POINT_DISTANCE
            )

            if (
                hands_close
                or points_close
            ):

                self._clap_stage = (
                    "CONTACT"
                )

                self._contact_started_at = (
                    now
                )

                self._last_gesture = (
                    "CONTACT"
                )

            return

        # ----------------------------------------------------
        # CONTACT
        # ----------------------------------------------------

        if (
            self._clap_stage
            == "CONTACT"
        ):

            self._last_gesture = (
                "CONTACT"
            )

            elapsed = (
                now
                - self._contact_started_at
            )

            if (
                elapsed
                > CLAP_RELEASE_TIMEOUT
            ):

                self._reset_clap()

                return

            if (
                self._center_distance
                >= CLAP_RELEASE_DISTANCE
            ):

                self._clap_detected()

    # ========================================================
    # CLAP DETECTED
    # ========================================================

    def _clap_detected(
        self,
    ) -> None:

        self._last_clap_time = (
            time.monotonic()
        )

        self._clap_stage = (
            "WAIT_OPEN"
        )

        self._last_gesture = (
            "CLAP DETECTED"
        )

        print()
        print(
            "================================="
        )

        print(
            "CLAP DETECTED"
        )

        print(
            "================================="
        )

        print()

        self._execute_work_mode()

    # ========================================================
    # RESET CLAP
    # ========================================================

    def _reset_clap(
        self,
    ) -> None:

        self._clap_stage = (
            "WAIT_OPEN"
        )

        self._ready_started_at = (
            0.0
        )

        self._contact_started_at = (
            0.0
        )

    # ========================================================
    # WORK MODE
    # ========================================================

    def _execute_work_mode(
        self,
    ) -> None:

        command = (
            "modalità lavoro"
        )

        self._last_command = (
            "MODALITA LAVORO"
        )

        self._command_message = (
            "WORK MODE"
        )

        self._command_message_until = (
            time.monotonic()
            + 3.0
        )

        self._emit_status(
            force=True
        )

        print(
            "Invio comando a J.A.R.V.I.S.:"
        )

        print(
            command
        )

        # ----------------------------------------------------
        # GUI MODE
        # ----------------------------------------------------

        if (
            self._command_callback
            is not None
        ):

            try:

                self._command_callback(
                    command
                )

                self._jarvis_status = (
                    "ONLINE"
                )

                print(
                    "Comando inviato tramite "
                    "VisionBridge."
                )

                return

            except Exception as error:

                print(
                    "Errore command callback:"
                )

                print(
                    error
                )

        # ----------------------------------------------------
        # STANDALONE FALLBACK
        # ----------------------------------------------------

        success = (
            self._send_command_to_jarvis(
                command
            )
        )

        if success:

            self._jarvis_status = (
                "ONLINE"
            )

        else:

            self._jarvis_status = (
                "OFFLINE"
            )

    # ========================================================
    # STANDALONE API
    # ========================================================

    def _send_command_to_jarvis(
        self,
        command: str,
    ) -> bool:

        payload = {
            "command": command,
        }

        body = (
            json.dumps(
                payload
            )
            .encode(
                "utf-8"
            )
        )

        request = (
            Request(
                JARVIS_API_URL,
                data=body,
                headers={
                    "Content-Type":
                        "application/json",
                },
                method="POST",
            )
        )

        try:

            with urlopen(
                request,
                timeout=JARVIS_API_TIMEOUT,
            ) as response:

                status_code = (
                    response.status
                )

                response.read()

            if (
                200
                <= status_code
                < 300
            ):

                print(
                    "Comando ricevuto "
                    "da J.A.R.V.I.S."
                )

                return True

            return False

        except HTTPError as error:

            print(
                "Errore HTTP J.A.R.V.I.S.:"
            )

            print(
                error.code,
                error.reason,
            )

            return False

        except URLError as error:

            print(
                "J.A.R.V.I.S. non raggiungibile:"
            )

            print(
                error.reason
            )

            return False

        except TimeoutError:

            print(
                "Timeout comunicazione "
                "con J.A.R.V.I.S."
            )

            return False

        except Exception as error:

            print(
                "Errore comunicazione "
                "con J.A.R.V.I.S.:"
            )

            print(
                error
            )

            return False

    # ========================================================
    # HAND CENTER
    # ========================================================

    @staticmethod
    def _hand_center(
        hand,
    ) -> tuple[
        float,
        float,
    ]:

        important_points = [
            0,
            5,
            9,
            13,
            17,
        ]

        x = (
            sum(
                hand[index].x
                for index
                in important_points
            )
            / len(
                important_points
            )
        )

        y = (
            sum(
                hand[index].y
                for index
                in important_points
            )
            / len(
                important_points
            )
        )

        return (
            x,
            y,
        )

    # ========================================================
    # MINIMUM HAND DISTANCE
    # ========================================================

    @staticmethod
    def _minimum_hand_distance(
        first_hand,
        second_hand,
    ) -> float:

        minimum = (
            float("inf")
        )

        for first in first_hand:

            for second in second_hand:

                distance = (
                    math.sqrt(
                        (
                            first.x
                            - second.x
                        ) ** 2
                        +
                        (
                            first.y
                            - second.y
                        ) ** 2
                    )
                )

                if (
                    distance
                    < minimum
                ):

                    minimum = (
                        distance
                    )

        return minimum

    # ========================================================
    # POINT DISTANCE
    # ========================================================

    @staticmethod
    def _point_distance(
        first,
        second,
    ) -> float:

        return (
            math.sqrt(
                (
                    first[0]
                    - second[0]
                ) ** 2
                +
                (
                    first[1]
                    - second[1]
                ) ** 2
            )
        )

    # ========================================================
    # DRAW HAND
    # ========================================================

    @staticmethod
    def _draw_hand(
        frame,
        landmarks,
    ) -> None:

        height, width, _ = (
            frame.shape
        )

        connections = [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),

            (0, 5),
            (5, 6),
            (6, 7),
            (7, 8),

            (5, 9),
            (9, 10),
            (10, 11),
            (11, 12),

            (9, 13),
            (13, 14),
            (14, 15),
            (15, 16),

            (13, 17),
            (17, 18),
            (18, 19),
            (19, 20),

            (0, 17),
        ]

        points = []

        for landmark in landmarks:

            x = int(
                landmark.x
                * width
            )

            y = int(
                landmark.y
                * height
            )

            points.append(
                (
                    x,
                    y,
                )
            )

        for start, end in connections:

            cv2.line(
                frame,
                points[start],
                points[end],
                (
                    0,
                    200,
                    255,
                ),
                2,
            )

        for point in points:

            cv2.circle(
                frame,
                point,
                4,
                (
                    0,
                    255,
                    255,
                ),
                -1,
            )

    # ========================================================
    # VIDEO OVERLAY
    # ========================================================

    def _draw_interface(
        self,
        frame,
        hand_count: int,
    ) -> None:

        height, _, _ = (
            frame.shape
        )

        cv2.putText(
            frame,
            (
                "J.A.R.V.I.S. // "
                "VISION CONTROL V5"
            ),
            (
                20,
                35,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (
                0,
                255,
                255,
            ),
            2,
        )

        cv2.putText(
            frame,
            (
                "CAMERA // "
                + (
                    "ONLINE"
                    if self._camera_online
                    else "OFFLINE"
                )
            ),
            (
                20,
                70,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (
                0,
                255,
                0,
            ),
            2,
        )

        cv2.putText(
            frame,
            (
                "HANDS // "
                f"{hand_count}"
            ),
            (
                20,
                100,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (
                220,
                220,
                220,
            ),
            2,
        )

        cv2.putText(
            frame,
            (
                "GESTURE // "
                + self._last_gesture
            ),
            (
                20,
                130,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (
                0,
                255,
                255,
            ),
            2,
        )

        cv2.putText(
            frame,
            (
                "COMMAND // "
                + self._last_command
            ),
            (
                20,
                160,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (
                255,
                255,
                255,
            ),
            2,
        )

        cv2.putText(
            frame,
            (
                "CENTER DIST // "
                f"{self._center_distance:.3f}"
            ),
            (
                20,
                190,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (
                180,
                220,
                220,
            ),
            1,
        )

        cv2.putText(
            frame,
            (
                "MIN DIST // "
                f"{self._minimum_distance:.3f}"
            ),
            (
                20,
                215,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (
                180,
                220,
                220,
            ),
            1,
        )

        if (
            time.monotonic()
            < self._command_message_until
        ):

            cv2.putText(
                frame,
                self._command_message,
                (
                    20,
                    255,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.85,
                (
                    0,
                    255,
                    0,
                ),
                2,
            )

        cv2.putText(
            frame,
            (
                "CLAP = WORK MODE"
            ),
            (
                20,
                height - 25,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (
                180,
                180,
                180,
            ),
            1,
        )


def main() -> None:

    controller = (
        GestureController(
            show_window=True,
        )
    )

    controller.run()


if __name__ == "__main__":
    main()