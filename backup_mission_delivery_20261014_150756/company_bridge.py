"""Bridge dedicato alla pagina 09 COMPANY; riusa Assistant.company."""
from __future__ import annotations

import threading
from PySide6.QtCore import QObject, Signal, Slot


class CompanyBridge(QObject):
    agentsChanged = Signal(list)
    missionEvent = Signal(dict)
    missionFinished = Signal(dict)
    missionBusyChanged = Signal(bool)

    def __init__(self, assistant):
        super().__init__()
        self._company = assistant.company
        self._lock = threading.Lock()
        self._busy = False

    @Slot()
    def refreshAgents(self):
        agents = []
        for agent in self._company.get_agents():
            agents.append({
                "id": str(agent.agent_id),
                "name": str(agent.name),
                "department": str(agent.department),
                "enabled": bool(getattr(agent, "enabled", True)),
            })
        self.agentsChanged.emit(agents)

    @Slot(str)
    def startMission(self, task):
        task = task.strip()
        if not task:
            self.missionEvent.emit({"event": "error", "message": "Inserisci una missione."})
            return
        with self._lock:
            if self._busy:
                self.missionEvent.emit({"event": "error", "message": "Missione gia in corso."})
                return
            self._busy = True
        self.missionBusyChanged.emit(True)
        threading.Thread(target=self._worker, args=(task,), daemon=True, name="CompanyMission").start()

    def _worker(self, task):
        try:
            self.missionEvent.emit({"event": "mission_started", "message": task})
            result = self._company.execute_auto(task, event_callback=self.missionEvent.emit)
            if result.mode == "single":
                single = result.single_result
                summary = getattr(single, "response", "") if single else ""
                agent_id = getattr(single, "agent_id", "") if single else ""
                self.missionEvent.emit({"event": "agent_completed", "agent_id": str(agent_id), "success": result.success, "message": summary[:250]})
            else:
                workflow = result.workflow_result
                summary = "\n\n".join(f"{s.agent_name}: {s.response}" for s in workflow.steps) if workflow else ""
            self.missionFinished.emit({"success": result.success, "mode": result.mode, "response": summary})
        except Exception as exc:
            self.missionEvent.emit({"event": "error", "message": str(exc)})
            self.missionFinished.emit({"success": False, "mode": "error", "response": str(exc)})
        finally:
            with self._lock:
                self._busy = False
            self.missionBusyChanged.emit(False)
