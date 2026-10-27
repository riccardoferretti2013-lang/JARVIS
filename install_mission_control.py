from pathlib import Path
from datetime import datetime
import shutil
import sys

root = Path.cwd()
source = Path(__file__).resolve().parent / 'CompanyPage.qml'
target = root / 'src' / 'jarvis' / 'gui_qml' / 'qml' / 'CompanyPage.qml'
if not target.is_file() or not (root / 'qml_main.py').is_file():
    sys.exit('ERRORE: apri PowerShell nella cartella principale di J.A.R.V.I.S. Nessun file modificato.')
if not source.is_file():
    sys.exit('ERRORE: CompanyPage.qml non trovato accanto allo script. Nessun file modificato.')
current = target.read_text(encoding='utf-8')
if 'companyBridge' not in current:
    sys.exit('ERRORE: versione COMPANY LIVE non rilevata. Nessun file modificato.')
backup = target.with_name('CompanyPage_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.qml')
shutil.copy2(target, backup)
shutil.copy2(source, target)
print('MISSION CONTROL installato correttamente.')
print('Backup:', backup)
print('Avvio: python qml_main.py')
