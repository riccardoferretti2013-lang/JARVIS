from pathlib import Path

from PyInstaller.utils.hooks import (
    collect_all,
    collect_submodules,
)


PROJECT_ROOT = Path(SPECPATH)

QML_DIR = (
    PROJECT_ROOT
    / "src"
    / "jarvis"
    / "gui_qml"
    / "qml"
)

ASSETS_DIR = (
    PROJECT_ROOT
    / "assets"
)

CONFIG_DIR = (
    PROJECT_ROOT
    / "config"
)

DATA_DIR = (
    PROJECT_ROOT
    / "data"
)

GESTURES_DIR = (
    PROJECT_ROOT
    / "src"
    / "jarvis"
    / "computer"
    / "gestures"
)

HAND_LANDMARKER_MODEL = (
    GESTURES_DIR
    / "hand_landmarker.task"
)

ICON_FILE = (
    PROJECT_ROOT
    / "assets"
    / "icons"
    / "jarvis.ico"
)


datas = []
binaries = []
hiddenimports = []


# =========================================================
# J.A.R.V.I.S. QML
# =========================================================

if QML_DIR.exists():

    datas.append(
        (
            str(QML_DIR),
            "src/jarvis/gui_qml/qml",
        )
    )


# =========================================================
# MEDIAPIPE HAND LANDMARKER MODEL
# =========================================================

if HAND_LANDMARKER_MODEL.exists():

    datas.append(
        (
            str(
                HAND_LANDMARKER_MODEL
            ),
            "src/jarvis/computer/gestures",
        )
    )


# =========================================================
# ASSETS
# =========================================================

if ASSETS_DIR.exists():

    datas.append(
        (
            str(ASSETS_DIR),
            "assets",
        )
    )


# =========================================================
# CONFIG
# =========================================================

if CONFIG_DIR.exists():

    datas.append(
        (
            str(CONFIG_DIR),
            "config",
        )
    )


# =========================================================
# DATA
# =========================================================

if DATA_DIR.exists():

    datas.append(
        (
            str(DATA_DIR),
            "data",
        )
    )


# =========================================================
# PYSIDE6
# =========================================================

qt_datas, qt_binaries, qt_hidden = (
    collect_all(
        "PySide6"
    )
)

datas += qt_datas
binaries += qt_binaries
hiddenimports += qt_hidden


# =========================================================
# TKINTER
# =========================================================

try:

    (
        tkinter_datas,
        tkinter_binaries,
        tkinter_hidden,
    ) = collect_all(
        "tkinter"
    )

    datas += tkinter_datas
    binaries += tkinter_binaries
    hiddenimports += tkinter_hidden

except Exception:

    pass


try:

    hiddenimports += (
        collect_submodules(
            "tkinter"
        )
    )

except Exception:

    pass


hiddenimports += [
    "tkinter",
    "tkinter.ttk",
    "tkinter.messagebox",
    "tkinter.filedialog",
    "tkinter.simpledialog",
    "_tkinter",
]


# =========================================================
# PIPER
# =========================================================

try:

    (
        piper_datas,
        piper_binaries,
        piper_hidden,
    ) = collect_all(
        "piper"
    )

    datas += piper_datas
    binaries += piper_binaries
    hiddenimports += piper_hidden

except Exception:

    pass


# =========================================================
# ONNXRUNTIME
# =========================================================

try:

    (
        onnx_datas,
        onnx_binaries,
        onnx_hidden,
    ) = collect_all(
        "onnxruntime"
    )

    datas += onnx_datas
    binaries += onnx_binaries
    hiddenimports += onnx_hidden

except Exception:

    pass


# =========================================================
# OPENWAKEWORD
# =========================================================

try:

    (
        wake_datas,
        wake_binaries,
        wake_hidden,
    ) = collect_all(
        "openwakeword"
    )

    datas += wake_datas
    binaries += wake_binaries
    hiddenimports += wake_hidden

except Exception:

    pass


# =========================================================
# FASTER WHISPER
# =========================================================

for module_name in [
    "faster_whisper",
    "ctranslate2",
    "tokenizers",
]:

    try:

        (
            module_datas,
            module_binaries,
            module_hidden,
        ) = collect_all(
            module_name
        )

        datas += module_datas
        binaries += module_binaries
        hiddenimports += module_hidden

    except Exception:

        pass


# =========================================================
# MEDIAPIPE
# =========================================================

try:

    (
        mediapipe_datas,
        mediapipe_binaries,
        mediapipe_hidden,
    ) = collect_all(
        "mediapipe"
    )

    datas += mediapipe_datas
    binaries += mediapipe_binaries
    hiddenimports += mediapipe_hidden

except Exception:

    pass


try:

    hiddenimports += (
        collect_submodules(
            "mediapipe"
        )
    )

except Exception:

    pass


# =========================================================
# OPENCV
# =========================================================

try:

    (
        opencv_datas,
        opencv_binaries,
        opencv_hidden,
    ) = collect_all(
        "cv2"
    )

    datas += opencv_datas
    binaries += opencv_binaries
    hiddenimports += opencv_hidden

except Exception:

    pass


try:

    hiddenimports += (
        collect_submodules(
            "cv2"
        )
    )

except Exception:

    pass


# =========================================================
# IMPORT DINAMICI
# =========================================================

for module_name in [
    "numpy",
    "scipy",
    "sounddevice",
    "psutil",
    "keyboard",
]:

    try:

        hiddenimports += (
            collect_submodules(
                module_name
            )
        )

    except Exception:

        pass


# =========================================================
# J.A.R.V.I.S. VISION MODULES
# =========================================================

hiddenimports += [
    "src.jarvis.gui_qml.vision_bridge",
    "src.jarvis.computer.gestures",
    "src.jarvis.computer.gestures.gesture_controller",
]


# =========================================================
# EXTRA HIDDEN IMPORTS
# =========================================================

hiddenimports += [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtQml",
    "PySide6.QtQuick",
    "PySide6.QtQuickControls2",

    "numpy",

    "sounddevice",

    "scipy",
    "scipy.io",
    "scipy.io.wavfile",

    "psutil",
    "keyboard",

    "mediapipe",
    "cv2",

    "tkinter",
    "_tkinter",
]


# =========================================================
# ANALYSIS
# =========================================================

a = Analysis(
    [
        str(
            PROJECT_ROOT
            / "qml_main.py"
        )
    ],
    pathex=[
        str(
            PROJECT_ROOT
        )
    ],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)


# =========================================================
# PYZ
# =========================================================

pyz = PYZ(
    a.pure
)


# =========================================================
# EXE
# =========================================================

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="J.A.R.V.I.S",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon=str(
        ICON_FILE
    ),
)


# =========================================================
# COLLECT
# =========================================================

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="J.A.R.V.I.S",
)