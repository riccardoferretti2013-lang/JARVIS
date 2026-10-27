
from pathlib import Path
from datetime import datetime
import ast
import re
import shutil

ROOT = Path(__file__).resolve().parent
QML = ROOT / "src/jarvis/gui_qml/qml/CompanyPage.qml"
BRIDGE = ROOT / "src/jarvis/gui_qml/company_bridge.py"

if not QML.is_file() or not BRIDGE.is_file():
    raise SystemExit("ERRORE: file del progetto non trovati.")

q = QML.read_text(encoding="utf-8")
b = BRIDGE.read_text(encoding="utf-8")

if "programFilePath" in q or "programLaunchResult" in b:
    raise SystemExit(
        "Modifica gia presente o installazione parziale. "
        "Nessun file modificato."
    )


def replace_one(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise RuntimeError(
            f"{label}: trovate {n} corrispondenze, attesa 1. "
            "Nessun file modificato."
        )
    return text.replace(old, new, 1)


# ======================================================
# COMPANY BRIDGE - IMPORT
# ======================================================

if "import subprocess" not in b:
    b = "import subprocess\n" + b

if "import sys" not in b:
    b = "import sys\n" + b

if "import ast" not in b:
    b = "import ast\n" + b

# Manteniamo eventuali import __future__ in prima posizione.
lines = b.splitlines(keepends=True)
added = []
while lines and lines[0] in (
    "import ast\n", "import subprocess\n", "import sys\n"
):
    added.append(lines.pop(0))

future_end = 0
for i, line in enumerate(lines):
    if line.startswith("from __future__ import "):
        future_end = i + 1

lines[future_end:future_end] = added
b = "".join(lines)

b = replace_one(
    b,
    "    missionDelivery = Signal(dict)",
    "    missionDelivery = Signal(dict)\n"
    "    programLaunchResult = Signal(dict)",
    "Segnale backend"
)

method = '''
    @Slot(str)
    def launchProgram(self, file_path):
        try:
            base = (
                self._project_root
                / "projects"
                / "company_missions"
            ).resolve()

            path = Path(file_path).resolve(strict=True)

            if (
                path.name != "main.py"
                or path.parent.parent != base
                or not path.is_file()
            ):
                raise ValueError("Percorso non autorizzato")

            ast.parse(
                path.read_text(encoding="utf-8"),
                filename=str(path)
            )

            subprocess.Popen(
                [sys.executable, str(path)],
                cwd=str(path.parent)
            )

            self.programLaunchResult.emit({
                "success": True,
                "message": "Programma avviato correttamente."
            })

        except Exception as exc:
            self.programLaunchResult.emit({
                "success": False,
                "message": "Errore avvio: " + str(exc)
            })

'''

b = replace_one(
    b,
    "    def _worker(",
    method + "    def _worker(",
    "Metodo avvio backend"
)

ast.parse(b)

# ======================================================
# COMPANY PAGE - PROPRIETA
# ======================================================

q = replace_one(
    q,
    '    property string deliverySummary: ""',
    '''    property string deliverySummary: ""
    property string programFilePath: ""
    property string programLaunchMessage: ""''',
    "Proprieta QML"
)

# ======================================================
# RESET NUOVA MISSIONE
# ======================================================

q = replace_one(
    q,
    '        companyPage.deliverySummary = ""',
    '''        companyPage.deliverySummary = ""
        companyPage.programFilePath = ""
        companyPage.programLaunchMessage = ""
        companyPage.lastMissionSuccess = false''',
    "Reset missione"
)

# ======================================================
# RICONOSCIMENTO PROGRAMMA CONSEGNATO
# ======================================================

q = replace_one(
    q,
    "            companyPage.deliverySummary = details",
    '''            companyPage.deliverySummary = details
            companyPage.programFilePath = ""

            if (data.status === "created" && data.files) {
                for (var i = 0; i < data.files.length; i++) {
                    var file = data.files[i]
                    if (file.name === "main.py"
                            && file.status === "syntax_ok") {
                        companyPage.programFilePath = file.path
                        break
                    }
                }
            }''',
    "Consegna programma"
)

# ======================================================
# REPORT: NON MOSTRARE IL CODICE PYTHON
# ======================================================

q = replace_one(
    q,
    'companyPage.lastResult = data.response || "Nessun risultato testuale"',
    '''companyPage.lastResult = data.success
                ? "Missione completata.\\\\n\\\\n" +
                  (companyPage.programFilePath.length > 0
                   ? "Programma Python pronto.\\\\n" +
                     "Premi AVVIA PROGRAMMA per eseguirlo."
                   : "Nessun programma avviabile consegnato.")
                : "Missione terminata con errori.\\\\n\\\\n" +
                  (companyPage.deliverySummary ||
                   "Controlla la timeline della missione.")''',
    "Report missione"
)

# ======================================================
# RICEZIONE RISULTATO AVVIO
# ======================================================

q = replace_one(
    q,
    "        function onMissionFinished(data) {",
    '''        function onProgramLaunchResult(data) {
            companyPage.programLaunchMessage = data.message || ""
        }

        function onMissionFinished(data) {''',
    "Evento avvio"
)

# ======================================================
# PULSANTE: INSERIMENTO PRIMA DELLA RIGA 383
# ======================================================

anchor = (
    "                    RowLayout { Layout.fillWidth: true\n"
    "                        Text { text: companyPage.deliverySummary"
)

button = '''
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 46
                        radius: 7
                        color: launchMouse.containsMouse
                               ? "#087E9C" : "#07536B"
                        border.color: "#38C9E9"

                        visible: companyPage.lastMissionSuccess
                                 && companyPage.programFilePath.length > 0

                        Text {
                            anchors.centerIn: parent
                            text: "AVVIA PROGRAMMA"
                            color: "#E8FCFF"
                            font.pixelSize: 13
                            font.bold: true
                            font.letterSpacing: 1
                        }

                        MouseArea {
                            id: launchMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: launchConfirm.open()
                        }
                    }

                    Text {
                        Layout.fillWidth: true
                        visible: companyPage.programLaunchMessage.length > 0
                        text: companyPage.programLaunchMessage
                        color: "#8CE8C6"
                        font.pixelSize: 11
                        wrapMode: Text.WordWrap
                    }

'''

# Normalizziamo solo i fine-riga in memoria.
q = q.replace("\r\n", "\n")

q = replace_one(
    q,
    anchor,
    button + anchor,
    "Pulsante nella zona RISULTATO"
)

# ======================================================
# FINESTRA DI CONFERMA
# ======================================================

dialog = '''
    Dialog {
        id: launchConfirm
        title: "CONFERMA AVVIO PROGRAMMA"
        modal: true
        anchors.centerIn: parent
        width: Math.min(companyPage.width - 40, 440)
        standardButtons: Dialog.Ok | Dialog.Cancel

        onAccepted: {
            if (companyPage.programFilePath.length > 0) {
                companyBridge.launchProgram(
                    companyPage.programFilePath
                )
            }
        }

        contentItem: Text {
            text: "Vuoi avviare il programma generato?\\\\n\\\\n" +
                  "Il codice AI potrebbe contenere operazioni non sicure."
            color: "#DDF7FF"
            wrapMode: Text.WordWrap
            padding: 16
        }

        background: Rectangle {
            color: "#092231"
            border.color: "#31B9D9"
            radius: 8
        }
    }
'''

# Inseriamo il Dialog prima dell'ultima graffa
# che chiude l'Item principale.
last_brace = q.rstrip().rfind("}")

if last_brace < 0:
    raise RuntimeError("Chiusura QML non trovata.")

q = q[:last_brace] + dialog + "\n" + q[last_brace:]

# ======================================================
# CONTROLLI PRE-INSTALLAZIONE
# ======================================================

def balanced_braces(source):
    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    i = 0

    while i < len(source):
        c = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ""

        if line_comment:
            if c == "\n":
                line_comment = False
            i += 1
            continue

        if block_comment:
            if c == "*" and nxt == "/":
                block_comment = False
                i += 2
            else:
                i += 1
            continue

        if quote:
            if escaped:
                escaped = False
            elif c == "\\":
                escaped = True
            elif c == quote:
                quote = None
            i += 1
            continue

        if c == "/" and nxt == "/":
            line_comment = True
            i += 2
            continue

        if c == "/" and nxt == "*":
            block_comment = True
            i += 2
            continue

        if c in ('"', "'"):
            quote = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth < 0:
                return False

        i += 1

    return depth == 0 and quote is None and not block_comment


if not balanced_braces(q):
    raise RuntimeError(
        "Controllo parentesi QML fallito. Nessun file modificato."
    )

# ======================================================
# BACKUP E SCRITTURA
# ======================================================

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / "backups" / ("mission_result_" + stamp)
backup.mkdir(parents=True, exist_ok=False)

shutil.copy2(QML, backup / "CompanyPage.qml")
shutil.copy2(BRIDGE, backup / "company_bridge.py")

try:
    BRIDGE.write_text(b, encoding="utf-8")
    QML.write_text(q, encoding="utf-8")
except Exception:
    shutil.copy2(backup / "CompanyPage.qml", QML)
    shutil.copy2(backup / "company_bridge.py", BRIDGE)
    raise

print()
print("======================================")
print("MISSION CONTROL - MODIFICA INSTALLATA")
print("======================================")
print("Backup:", backup)
print("Pulsante AVVIA PROGRAMMA aggiunto.")
print("Codice Python nascosto dal report.")
print("Conferma richiesta prima dell'avvio.")
