"""Patch minimo e con backup. Eseguire dalla root JARVIS: python install_company.py"""
from pathlib import Path
import shutil
import sys
from datetime import datetime

ROOT = Path.cwd()
PACKAGE = Path(__file__).resolve().parent
TARGETS = {
    "workflow": ROOT / "src/jarvis/agents/workflow_manager.py",
    "manager": ROOT / "src/jarvis/agents/company_manager.py",
    "main": ROOT / "qml_main.py",
    "page": ROOT / "src/jarvis/gui_qml/qml/CompanyPage.qml",
}
BRIDGE = ROOT / "src/jarvis/gui_qml/company_bridge.py"

def replace_once(text, before, after, label):
    count = text.count(before)
    if count != 1:
        raise RuntimeError(f"{label}: attesa 1 occorrenza, trovate {count}. Nessuna modifica effettuata.")
    return text.replace(before, after, 1)

def patch_workflow(t):
    t = replace_once(t, '    def execute(\n        self,\n        task: str,\n    ) -> WorkflowResult:', '    def execute(\n        self,\n        task: str,\n        event_callback=None,\n    ) -> WorkflowResult:', 'WorkflowManager.execute')
    t = replace_once(t, '        plan = (\n            self.create_plan(\n                task\n            )\n        )\n\n        workflow =', '        plan = (\n            self.create_plan(\n                task\n            )\n        )\n\n        if event_callback is not None:\n            event_callback({"event": "plan_created", "total": len(plan.tasks)})\n\n        workflow =', 'workflow plan')
    t = replace_once(t, '        for planned_task in plan.tasks:\n\n            agent =', '        for planned_task in plan.tasks:\n\n            if event_callback is not None:\n                event_callback({"event": "agent_started", "agent_id": planned_task.agent_id, "task_id": planned_task.task_id})\n\n            agent =', 'workflow step start')
    t = replace_once(t, '                workflow.steps.append(\n                    step\n                )\n\n                continue', '                workflow.steps.append(\n                    step\n                )\n                if event_callback is not None:\n                    event_callback({"event": "agent_completed", "agent_id": step.agent_id, "task_id": step.task_id, "success": False, "message": step.error or ""})\n\n                continue', 'workflow missing agent')
    t = replace_once(t, '            workflow.steps.append(\n                step\n            )\n\n            previous_results.append(', '            workflow.steps.append(\n                step\n            )\n            if event_callback is not None:\n                event_callback({"event": "agent_completed", "agent_id": step.agent_id, "task_id": step.task_id, "success": step.success, "message": (step.error or step.response)[:250]})\n\n            previous_results.append(', 'workflow step complete')
    return t

def patch_manager(t):
    t = replace_once(t, '    def execute_workflow(\n        self,\n        task: str,\n    ) -> WorkflowResult:', '    def execute_workflow(\n        self,\n        task: str,\n        event_callback=None,\n    ) -> WorkflowResult:', 'CompanyManager.execute_workflow')
    t = replace_once(t, '            .execute(task)\n        )', '            .execute(task, event_callback=event_callback)\n        )', 'CompanyManager workflow call')
    t = replace_once(t, '    def execute_auto(\n        self,\n        task: str,\n    ) -> CompanyExecutionResult:', '    def execute_auto(\n        self,\n        task: str,\n        event_callback=None,\n    ) -> CompanyExecutionResult:', 'CompanyManager.execute_auto')
    t = replace_once(t, '                self.execute_workflow(\n                    task\n                )', '                self.execute_workflow(\n                    task,\n                    event_callback=event_callback,\n                )', 'CompanyManager execute auto workflow')
    t = replace_once(t, '        single_result = (\n            self.execute_task(\n                task\n            )\n        )', '        if event_callback is not None:\n            event_callback({"event": "single_started", "message": "Esecuzione agente singolo"})\n        single_result = (\n            self.execute_task(\n                task\n            )\n        )', 'CompanyManager execute auto single')
    return t

def patch_main(t):
    t = replace_once(t, 'from src.jarvis.gui_qml.vision_bridge import (\n    VisionBridge,\n)', 'from src.jarvis.gui_qml.vision_bridge import (\n    VisionBridge,\n)\nfrom src.jarvis.gui_qml.company_bridge import CompanyBridge', 'qml_main import')
    t = replace_once(t, '    # ========================================================\n    # VISION\n', '    company_bridge = CompanyBridge(assistant)\n\n    # ========================================================\n    # VISION\n', 'qml_main instance')
    t = replace_once(t, '    engine.rootContext().setContextProperty(\n        "visionBridge",\n        vision_bridge,\n    )', '    engine.rootContext().setContextProperty(\n        "visionBridge",\n        vision_bridge,\n    )\n\n    engine.rootContext().setContextProperty(\n        "companyBridge",\n        company_bridge,\n    )', 'qml_main context')
    return t

def main():
    for name, path in TARGETS.items():
        if not path.is_file():
            raise RuntimeError(f"File mancante: {path}")
    if BRIDGE.exists():
        raise RuntimeError(f"{BRIDGE} esiste gia: controllalo manualmente prima di procedere.")
    original = {key: path.read_text(encoding="utf-8") for key, path in TARGETS.items()}
    updated = {
        "workflow": patch_workflow(original["workflow"]),
        "manager": patch_manager(original["manager"]),
        "main": patch_main(original["main"]),
        "page": (PACKAGE / "CompanyPage.qml").read_text(encoding="utf-8"),
    }
    import ast
    for name in ("workflow", "manager", "main"):
        ast.parse(updated[name], filename=str(TARGETS[name]))
    ast.parse((PACKAGE / "company_bridge.py").read_text(encoding="utf-8"))
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ROOT / f"backup_company_{stamp}"
    backup.mkdir()
    for key, path in TARGETS.items():
        shutil.copy2(path, backup / f"{key}_{path.name}")
    try:
        for key, path in TARGETS.items():
            path.write_text(updated[key], encoding="utf-8")
        shutil.copy2(PACKAGE / "company_bridge.py", BRIDGE)
    except Exception:
        for key, path in TARGETS.items():
            shutil.copy2(backup / f"{key}_{path.name}", path)
        if BRIDGE.exists():
            BRIDGE.unlink()
        raise
    print("COMPANY installata. Backup:", backup)
    print("Avvio: python qml_main.py")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("INSTALLAZIONE ANNULLATA:", exc)
        sys.exit(1)
