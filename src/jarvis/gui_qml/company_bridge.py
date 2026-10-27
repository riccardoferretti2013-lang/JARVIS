
"""
Bridge dedicato alla pagina 09 COMPANY.

Collega la GUI QML alla AI Company di J.A.R.V.I.S.
Gestisce:
- elenco agenti;
- avvio missioni;
- eventi in tempo reale;
- integrazione finale del CEO;
- consegna dei programmi Python;
- diagnostica e stato della missione.

Non esegue automaticamente il codice generato.
"""

from __future__ import annotations
import ast
import sys
import subprocess

import threading
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from .mission_delivery import deliver


class CompanyBridge(QObject):

    # ==========================================================
    # SEGNALI QML
    # ==========================================================

    agentsChanged = Signal(list)
    missionEvent = Signal(dict)
    missionFinished = Signal(dict)
    missionDelivery = Signal(dict)
    programLaunchResult = Signal(dict)
    missionBusyChanged = Signal(bool)

    # ==========================================================
    # INIZIALIZZAZIONE
    # ==========================================================

    def __init__(self, assistant):
        super().__init__()

        # Riutilizza la Company già presente nell'Assistant.
        self._company = assistant.company

        # Cartella principale del progetto J.A.R.V.I.S.
        self._project_root = Path(__file__).resolve().parents[3]

        self._lock = threading.Lock()
        self._busy = False

    # ==========================================================
    # ELENCO AGENTI
    # ==========================================================

    @Slot()
    def refreshAgents(self):
        try:
            agents = []

            for agent in self._company.get_agents():
                agents.append({
                    "agent_id": str(agent.agent_id),
                    "name": str(agent.name),
                    "role": str(agent.role),
                    "department": str(agent.department),
                    "description": str(agent.description or ""),
                    "provider": str(agent.preferred_provider or ""),
                    "model": str(agent.preferred_model or ""),
                    "enabled": bool(agent.enabled),
                    "priority": int(agent.priority),
                })

            self.agentsChanged.emit(agents)

        except Exception as exc:
            self.missionEvent.emit({
                "event": "error",
                "message": (
                    "Errore aggiornamento agenti: "
                    + str(exc)
                ),
            })

    # ==========================================================
    # AVVIO MISSIONE
    # ==========================================================

    @Slot(str)
    def startMission(self, task):
        task = str(task or "").strip()

        if not task:
            self.missionEvent.emit({
                "event": "error",
                "message": "Inserisci una missione valida.",
            })
            return

        with self._lock:
            if self._busy:
                self.missionEvent.emit({
                    "event": "error",
                    "message": "Una missione è già in esecuzione.",
                })
                return

            self._busy = True

        self.missionBusyChanged.emit(True)

        worker = threading.Thread(
            target=self._worker,
            args=(task,),
            daemon=True,
            name="JARVIS-Company-Mission",
        )

        worker.start()

    # ==========================================================
    # ESECUZIONE MISSIONE
    # ==========================================================


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

    def _worker(self, task):
        try:
            self.missionEvent.emit({
                "event": "mission_started",
                "message": task,
            })

            # Gli agenti eseguono la missione.
            # Il CEO integra i risultati.
            result = self._company.execute_auto(
                task,
                event_callback=self.missionEvent.emit,
            )

            # Mantiene l'evento dell'agente singolo.
            if result.mode == "single":
                single = result.single_result

                agent_id = (
                    getattr(single, "agent_id", "")
                    if single
                    else ""
                )

                agent_response = (
                    getattr(single, "response", "") or ""
                    if single
                    else ""
                )

                self.missionEvent.emit({
                    "event": "agent_completed",
                    "agent_id": str(agent_id),
                    "success": bool(
                        getattr(single, "success", False)
                    ),
                    "message": agent_response[:250],
                })

            # Risposta definitiva del CEO.
            final_text = result.final_response or ""

            # ==================================================
            # DIAGNOSTICA CEO
            # ==================================================

            print("\n" + "=" * 55)
            print("J.A.R.V.I.S. COMPANY - CEO")
            print("=" * 55)
            print("Modalità:", result.mode)
            print("Successo CEO:", result.success)
            print("Lunghezza risposta:", len(final_text))
            print("Anteprima risposta:")
            print(final_text[:1500])
            print("=" * 55 + "\n")

            # ==================================================
            # CONSEGNA PROGRAMMA
            # ==================================================

            if result.success:
                try:
                    delivery = deliver(
                        final_text,
                        self._project_root,
                    )

                except Exception as exc:
                    delivery = {
                        "status": "error",
                        "message": (
                            "Errore durante la consegna: "
                            + str(exc)
                        ),
                        "files": [],
                    }

            else:
                delivery = {
                    "status": "error",
                    "message": (
                        "Il CEO non ha completato "
                        "l'integrazione finale."
                    ),
                    "files": [],
                }

            self.missionDelivery.emit(delivery)

            # ==================================================
            # VERIFICA FILE CONSEGNATO
            # ==================================================

            files = delivery.get("files", [])

            delivery_ok = (
                delivery.get("status") == "created"
                and len(files) == 1
                and files[0].get("name") == "main.py"
                and files[0].get("status") == "syntax_ok"
            )

            mission_ok = (
                bool(result.success)
                and delivery_ok
            )

            # ==================================================
            # EVENTO RISULTATO CONSEGNA
            # ==================================================

            if delivery_ok:
                self.missionEvent.emit({
                    "event": "delivery_completed",
                    "message": (
                        "Programma main.py creato "
                        "e sintassi verificata."
                    ),
                })

            else:
                self.missionEvent.emit({
                    "event": "delivery_error",
                    "message": delivery.get(
                        "message",
                        "Programma finale non consegnato.",
                    ),
                })

            # ==================================================
            # RISULTATO FINALE MISSIONE
            # ==================================================

            if mission_ok:
                response = final_text

            else:
                response = (
                    "CONSEGNA NON COMPLETATA\n\n"
                    + delivery.get(
                        "message",
                        "Il programma non è stato generato.",
                    )
                    + "\n\n"
                    + final_text
                )

            self.missionFinished.emit({
                "success": mission_ok,
                "mode": result.mode,
                "response": response,
            })

        except Exception as exc:
            self.missionEvent.emit({
                "event": "error",
                "message": str(exc),
            })

            self.missionFinished.emit({
                "success": False,
                "mode": "error",
                "response": str(exc),
            })

        finally:
            with self._lock:
                self._busy = False

            self.missionBusyChanged.emit(False)
