'''Installazione prudente: integra CEO nella COMPANY esistente.'''
from pathlib import Path
from datetime import datetime
import shutil
import sys

ROOT = Path(__file__).resolve().parent
MANAGER = ROOT / 'src/jarvis/agents/company_manager.py'
BRIDGE = ROOT / 'src/jarvis/gui_qml/company_bridge.py'


def replace_once(src, old, new, label):
    count = src.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: attese 1 occorrenza, trovate {count}. Nessuna modifica effettuata.')
    return src.replace(old, new, 1)


def main():
    if not MANAGER.is_file() or not BRIDGE.is_file():
        raise RuntimeError('Esegui lo script dalla cartella principale di J.A.R.V.I.S.')
    m = MANAGER.read_text(encoding='utf-8')
    b = BRIDGE.read_text(encoding='utf-8')
    if 'def _integrate_as_ceo(' in m:
        print('CEO gia integrato. Nessuna modifica.'); return
    m = replace_once(m, 'from dataclasses import dataclass', 'from dataclasses import dataclass, replace', 'import dataclasses')
    m = replace_once(m, '    workflow_result: WorkflowResult | None = None\n', '    workflow_result: WorkflowResult | None = None\n    final_response: str = ""\n    final_success: bool | None = None\n', 'campi risultato')
    m = replace_once(m, '    def success(self) -> bool:\n\n        if self.mode == "single":', '    def success(self) -> bool:\n\n        if self.final_success is not None:\n            return self.final_success\n\n        if self.mode == "single":', 'proprieta success')
    old='''            return CompanyExecutionResult(
                mode="workflow",
                decision=decision,
                workflow_result=(
                    workflow_result
                ),
            )'''
    new='''            final_text, final_ok = self._integrate_as_ceo(task, workflow_result, event_callback)
            return CompanyExecutionResult(
                mode="workflow",
                decision=decision,
                workflow_result=workflow_result,
                final_response=final_text,
                final_success=final_ok,
            )'''
    m=replace_once(m,old,new,'workflow return')
    old='''        return CompanyExecutionResult(
            mode="single",
            decision=decision,
            single_result=(
                single_result
            ),
        )'''
    new='''        final_text, final_ok = self._integrate_as_ceo(task, single_result, event_callback)
        return CompanyExecutionResult(
            mode="single",
            decision=decision,
            single_result=single_result,
            final_response=final_text,
            final_success=final_ok,
        )'''
    m=replace_once(m,old,new,'single return')
    insertion='''    def _integrate_as_ceo(self, task, source_result, event_callback=None):
        # Il CEO integra i contributi degli agenti.
        def emit(event, **data):
            if event_callback is not None:
                event_callback({"event": event, **data})

        if hasattr(source_result, "steps"):
            contributions = [
                f"AGENTE {s.agent_name} (successo={s.success}):\\n{s.response}"
                for s in source_result.steps if s.response
            ]
        else:
            response = getattr(source_result, "response", "") or ""
            contributions = [f"AGENTE ESECUTORE:\\n{response}"] if response else []
        if not contributions:
            emit("ceo_error", message="Nessun contributo da integrare")
            return "Nessun contributo utile prodotto dagli agenti.", False

        ceo = next((a for a in self._registry.enabled()
                    if "jarvis" in a.name.lower().replace(".", "") or
                    "j.a.r.v.i.s" in a.name.lower()), None)
        if ceo is None:
            emit("ceo_error", message="Agente CEO J.A.R.V.I.S. non trovato")
            return "CEO J.A.R.V.I.S. non disponibile: nessun file consegnato.", False

        emit("ceo_started", agent_id=str(ceo.agent_id), message="Integrazione finale in corso")
        context = "\\n\\n".join(contributions)
        # Evita di passare al modello un contesto illimitato.
        context = context[-18000:]
        instruction = (
            "Sei J.A.R.V.I.S., CEO e integratore finale della AI Company.\\n"
            "MISSIONE ORIGINALE:\\n" + task + "\\n\\n"
            "CONTRIBUTI DEGLI AGENTI:\\n" + context + "\\n\\n"
            "Crea un PROGRAMMA DEFINITIVO, completo e coerente, non una spiegazione. "
            "Se il compito richiede una GUI, implementala realmente con PySide6. "
            "Rispondi con UN SOLO blocco Markdown ```python seguito dal codice COMPLETO "
            "di main.py e chiuso da ```. Non usare segnaposto, omissioni o puntini. "
            "Includi tutti gli import e l'entry point if __name__ == '__main__'. "
            "Se non puoi produrre un file completo, spiega l'impossibilita senza inventare codice."
        )
        try:
            # Mantiene il provider configurato per il CEO, aumentando il budget
            # di output per ridurre il rischio di troncamento.
            ceo_for_execution = replace(ceo, max_tokens=max(4096, ceo.max_tokens))
            result = self._workflow_manager.executor.execute(
                agent=ceo_for_execution, task=instruction
            )
            text = getattr(result, "response", "") or ""
            ok = bool(getattr(result, "success", False)) and bool(text.strip())
            emit("ceo_completed", agent_id=str(ceo.agent_id), success=ok,
                 message=(text[:250] if ok else (getattr(result, "error", "") or "CEO senza risposta")))
            return text, ok
        except Exception as exc:
            emit("ceo_error", message=str(exc))
            return f"Integrazione CEO fallita: {exc}", False

'''
    m=replace_once(m,'    def preview_workflow(\n',insertion+'    def preview_workflow(\n','inserimento metodo')
    old='''                summary = "\\n\\n".join(f"{s.agent_name}: {s.response}" for s in workflow.steps) if workflow else ""'''
    if old not in b:
        raise RuntimeError('Bridge diverso dal previsto: aggiornamento interrotto.')
    b=replace_once(b,old,old+'\n            summary = result.final_response or ""','bridge final response')
    # Non salvare una risposta CEO fallita come progetto.
    b=replace_once(b,'delivery = deliver(summary, self._project_root)',
                   'delivery = deliver(summary, self._project_root) if result.success else {"status": "error", "message": "CEO non ha completato la consegna", "files": []}',
                   'bridge delivery')
    compile(m, str(MANAGER), 'exec'); compile(b, str(BRIDGE), 'exec')
    backup=ROOT / ('backup_ceo_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
    backup.mkdir()
    shutil.copy2(MANAGER, backup / 'company_manager.py')
    shutil.copy2(BRIDGE, backup / 'company_bridge.py')
    try:
        MANAGER.write_text(m, encoding='utf-8')
        BRIDGE.write_text(b, encoding='utf-8')
    except Exception:
        shutil.copy2(backup / 'company_manager.py', MANAGER)
        shutil.copy2(backup / 'company_bridge.py', BRIDGE)
        raise
    print('CEO INTEGRATION installata. Backup:', backup)
    print('Nota: il controllo sintattico dei file avviene nel modulo MissionDelivery esistente.')

if __name__ == '__main__':
    try: main()
    except Exception as exc:
        print('INSTALLAZIONE INTERROTTA:', exc)
        sys.exit(1)
