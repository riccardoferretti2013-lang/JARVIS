"""Installer minimo con backup. Eseguire nella root JARVIS."""
from pathlib import Path
from datetime import datetime
import shutil
import sys

root = Path.cwd()
source = Path(__file__).resolve().parent
bridge = root / 'src/jarvis/gui_qml/company_bridge.py'
qml = root / 'src/jarvis/gui_qml/qml/CompanyPage.qml'
target_module = root / 'src/jarvis/gui_qml/mission_delivery.py'
if not (root / 'qml_main.py').is_file() or not bridge.is_file() or not qml.is_file():
    sys.exit('ERRORE: esegui dalla root JARVIS con COMPANY LIVE installata. Nessuna modifica.')
b = bridge.read_text(encoding='utf-8')
q = qml.read_text(encoding='utf-8')
if 'missionDelivery = Signal(dict)' in b:
    sys.exit('Gia installato. Nessuna modifica.')
needle = '    missionFinished = Signal(dict)'
worker = '            self.missionFinished.emit({"success": result.success, "mode": result.mode, "response": summary})'
if b.count(needle) != 1 or b.count(worker) != 1 or q.count('function onMissionFinished(data) {') != 1 or 'companyBridge' not in q:
    sys.exit('ERRORE: versione inattesa di COMPANY. Nessuna modifica.')
if target_module.exists():
    sys.exit('ERRORE: mission_delivery.py esiste gia. Nessuna modifica.')
newb = b.replace('import threading', 'import threading\nfrom pathlib import Path\nfrom .mission_delivery import deliver', 1)
newb = newb.replace(needle, needle + '\n    missionDelivery = Signal(dict)', 1)
newb = newb.replace('        self._company = assistant.company', '        self._company = assistant.company\n        self._project_root = Path(__file__).resolve().parents[3]', 1)
newb = newb.replace(worker, '''            try:
                delivery = deliver(summary, self._project_root)
                self.missionDelivery.emit(delivery)
            except Exception as delivery_exc:
                self.missionDelivery.emit({'status': 'error', 'message': str(delivery_exc), 'files': []})
''' + worker, 1)
newq = q.replace('    property string lastResult: ""', '    property string lastResult: ""\n    property string deliverySummary: ""', 1)
newq = newq.replace('        companyPage.lastResult = ""', '        companyPage.lastResult = ""\n        companyPage.deliverySummary = ""', 1)
newq = newq.replace('        function onMissionFinished(data) {', '''        function onMissionDelivery(data) {
            var details = data.message || ""
            if (data.folder) details += "\\nCartella: " + data.folder
            if (data.files) {
                for (var i = 0; i < data.files.length; ++i) {
                    var f = data.files[i]
                    details += "\\n" + f.name + " — " + f.status + (f.error ? " — " + f.error : "")
                }
            }
            companyPage.deliverySummary = details
        }
        function onMissionFinished(data) {''', 1)
old = 'Text { text: "Risposta degli agenti · nessun file viene creato automaticamente"; color: "#6E9CAD"; font.pixelSize: 9 }'
new = 'Text { text: companyPage.deliverySummary || "In attesa della consegna dei file Python"; color: "#6E9CAD"; font.pixelSize: 9; wrapMode: Text.WordWrap; Layout.fillWidth: true }'
if q.count(old) != 1:
    sys.exit('ERRORE: etichetta report non riconosciuta. Nessuna modifica.')
newq = newq.replace(old, new, 1)
backup = root / ('backup_mission_delivery_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir()
shutil.copy2(bridge, backup / 'company_bridge.py')
shutil.copy2(qml, backup / 'CompanyPage.qml')
try:
    shutil.copy2(source / 'mission_delivery.py', target_module)
    bridge.write_text(newb, encoding='utf-8')
    qml.write_text(newq, encoding='utf-8')
except Exception:
    shutil.copy2(backup / 'company_bridge.py', bridge)
    shutil.copy2(backup / 'CompanyPage.qml', qml)
    target_module.unlink(missing_ok=True)
    raise
print('Consegna file installata. Backup:', backup)
print('Avvia: python qml_main.py')
