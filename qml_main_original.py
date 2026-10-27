
"""
J.A.R.V.I.S.
GUI QML Launcher

Configurazione dello stile Qt Quick Controls
e avvio dell'applicazione originale.

Versione: 0.1 Alpha
"""

from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

ORIGINAL_LAUNCHER = (
    PROJECT_ROOT / "qml_main_original.py"
)


# ============================================================
# QT QUICK CONTROLS STYLE
# ============================================================

# Lo stile va configurato prima del caricamento
# dell'applicazione e dei componenti QML.

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"


# ============================================================
# STARTUP
# ============================================================

def main() -> None:

    print()
    print("=" * 55)
    print("J.A.R.V.I.S. // GUI INITIALIZATION")
    print("=" * 55)
    print()

    print("[GUI] Qt Quick Controls: Basic")
    print("[GUI] Project root:", PROJECT_ROOT)

    if not ORIGINAL_LAUNCHER.is_file():
        raise FileNotFoundError(
            "Launcher originale non trovato: "
            f"{ORIGINAL_LAUNCHER}"
        )

    print("[GUI] Launcher originale trovato")
    print("[GUI] Avvio J.A.R.V.I.S...")
    print()

    os.chdir(PROJECT_ROOT)

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(
            0,
            str(PROJECT_ROOT),
        )

    runpy.run_path(
        str(ORIGINAL_LAUNCHER),
        run_name="__main__",
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
