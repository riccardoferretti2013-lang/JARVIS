import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// COMPANY 09 only. Backend live state from companyBridge.
Item {
    id: companyPage
    property color accentColor: "#00D9FF"
    property int selectedOffice: -1
    property var offices: [
        {name:"RESEARCH HUB",role:"Ricerca e Internet",agent:"Research Analyst",x:0.12,y:0.18,w:0.22,h:0.19},
        {name:"PROJECT MANAGEMENT",role:"Strategia e Pianificazione",agent:"Project Manager",x:0.40,y:0.01,w:0.22,h:0.18},
        {name:"FRONTEND OFFICE",role:"GUI e Interfacce QML",agent:"Frontend Developer",x:0.75,y:0.18,w:0.23,h:0.19},
        {name:"BACKEND OFFICE",role:"Sviluppo API e Database",agent:"Backend Architect",x:0.08,y:0.38,w:0.23,h:0.19},
        {name:"CEO OFFICE",role:"J.A.R.V.I.S. / Coordinamento",agent:"J.A.R.V.I.S.",x:0.41,y:0.32,w:0.20,h:0.29},
        {name:"QA LAB",role:"Test e Qualita",agent:"QA Engineer",x:0.76,y:0.39,w:0.22,h:0.18},
        {name:"AUTOMATION ROOM",role:"Automazioni e Workflow",agent:"Automation Specialist",x:0.09,y:0.61,w:0.23,h:0.19},
        {name:"VISION LAB",role:"Visione e Analisi Immagini",agent:"Vision Specialist",x:0.76,y:0.61,w:0.21,h:0.19},
        {name:"MEMORY ARCHIVE",role:"Memoria e Conoscenza",agent:"Memory Manager",x:0.09,y:0.81,w:0.25,h:0.17},
        {name:"DATA CENTER",role:"Infrastruttura e Storage",agent:"System Manager",x:0.75,y:0.81,w:0.24,h:0.17}
    ]
    property var agents: []
    property var agentStates: ({})
    property bool missionBusy: false
    property string lastActivity: "In attesa di una missione"
    property string lastResult: ""
    property string deliverySummary: ""
    property string missionTitle: ""
    property var missionTimeline: []
    property int finishedSteps: 0
    property int totalSteps: 0
    property bool missionPanelOpen: false
    property int missionTab: 0
    property bool lastMissionSuccess: false
    function appendTimeline(eventName, agentName, detail, success) {
        var entries = companyPage.missionTimeline.slice()
        entries.push({kind: eventName, agent: agentName || "J.A.R.V.I.S.", detail: detail || "", success: success === true})
        companyPage.missionTimeline = entries
    }
    function launchMission() {
        var text = missionInput.text.trim()
        if (!text.length || companyPage.missionBusy) return
        companyPage.agentStates = ({})
        companyPage.missionTimeline = []
        companyPage.finishedSteps = 0
        companyPage.totalSteps = 0
        companyPage.lastResult = ""
        companyPage.deliverySummary = ""
        companyPage.missionTitle = text
        companyPage.missionTab = 1
        companyBridge.startMission(text)
    }
    function officeState(agentName) {
        var a = companyPage.agents
        for (var i = 0; i < a.length; i++) {
            if (a[i].name === agentName) return companyPage.agentStates[a[i].id] || "idle"
        }
        return "idle"
    }
    function stateColor(state) {
        return state === "working" ? "#00D9FF" : state === "completed" ? "#00E18A" : state === "error" ? "#FF607A" : "#D9A544"
    }
    Component.onCompleted: companyBridge.refreshAgents()
    Connections {
        target: companyBridge
        function onAgentsChanged(items) { companyPage.agents = items }
        function onMissionBusyChanged(busy) { companyPage.missionBusy = busy }
        function onMissionEvent(data) {
            var states = Object.assign({}, companyPage.agentStates)
            if (data.agent_id) {
                if (data.event === "agent_started") states[data.agent_id] = "working"
                if (data.event === "agent_completed") states[data.agent_id] = data.success ? "completed" : "error"
            }
            companyPage.agentStates = states
            if (data.event === "mission_started") {
                companyPage.lastActivity = "Missione avviata"
                companyPage.appendTimeline("start", "J.A.R.V.I.S.", "Missione ricevuta e assegnata al sistema", true)
            } else if (data.event === "plan_created") {
                companyPage.totalSteps = Number(data.total) || 0
                companyPage.lastActivity = "Piano: " + data.total + " attività"
                companyPage.appendTimeline("plan", "Project Manager", "Piano di " + data.total + " attività", true)
            } else if (data.event === "single_started") {
                companyPage.totalSteps = 1
                companyPage.lastActivity = "Agente singolo in esecuzione"
                companyPage.appendTimeline("working", "Agente selezionato", "Elaborazione in corso", false)
            } else if (data.event === "agent_started") {
                companyPage.lastActivity = "In lavorazione: " + data.agent_id
                companyPage.appendTimeline("working", data.agent_id, "Attività " + (data.task_id || "") + " avviata", false)
            } else if (data.event === "agent_completed") {
                companyPage.finishedSteps += 1
                companyPage.lastActivity = (data.success ? "Completato: " : "Errore: ") + data.agent_id
                companyPage.appendTimeline(data.success ? "done" : "error", data.agent_id, data.message || (data.success ? "Attività completata" : "Attività fallita"), data.success)
            } else if (data.event === "error") {
                companyPage.lastActivity = "Errore: " + data.message
                companyPage.appendTimeline("error", "J.A.R.V.I.S.", data.message, false)
            }
        }
        function onMissionDelivery(data) {
            var details = data.message || ""
            if (data.folder) details += "\nCartella: " + data.folder
            if (data.files) {
                for (var i = 0; i < data.files.length; ++i) {
                    var f = data.files[i]
                    details += "\n" + f.name + " — " + f.status + (f.error ? " — " + f.error : "")
                }
            }
            companyPage.deliverySummary = details
        }
        function onMissionFinished(data) {
            companyPage.lastResult = data.response || "Nessun risultato testuale"
            companyPage.lastActivity = data.success ? "Missione completata" : "Missione terminata con errori"
            companyPage.lastMissionSuccess = !!data.success
            companyPage.appendTimeline(data.success ? "done" : "error", "J.A.R.V.I.S.", data.success ? "Missione conclusa" : "Missione terminata con errori", data.success)
            companyPage.missionTab = 2
            companyPage.missionPanelOpen = true
        }
    }
    Rectangle { anchors.fill: parent; color: "#020911"; radius: 7; border.color: "#14506C" }
    ColumnLayout {
        anchors.fill: parent; anchors.margins: 7; spacing: 7
        Rectangle {
            Layout.fillWidth: true; Layout.preferredHeight: 49; radius: 5
            color: "#031523"; border.color: "#12516A"
            RowLayout {
                anchors.fill: parent; anchors.leftMargin: 16; anchors.rightMargin: 14
                ColumnLayout {
                    spacing: 2
                    Text { text: "HEADQUARTERS"; color: "#67E5FF"; font.pixelSize: 19; font.bold: true; font.letterSpacing: 2 }
                    Text { text: "INTELLIGENCE   ·   AUTOMATION   ·   DEVELOPMENT   ·   RESEARCH"; color: "#45A9C8"; font.pixelSize: 9; font.letterSpacing: 1 }
                }
                Item { Layout.fillWidth: true }
                Rectangle { width: 8; height: 8; radius: 4; color: "#00E18A" }
                Text { text: "COMPANY // LIVE"; color: "#8CB8C8"; font.pixelSize: 9 }
                Button {
                    text: companyPage.missionBusy ? "IN ESECUZIONE" : "+ MISSIONE"
                    enabled: !companyPage.missionBusy
                    onClicked: { companyPage.missionPanelOpen = true; companyPage.missionTab = companyPage.missionBusy ? 1 : 0 }
                }
            }
        }
        RowLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 7
            Rectangle {
                id: mapPanel
                Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumWidth: 280
                color: "#020B12"; radius: 5; border.color: "#16526B"; clip: true
                Image {
                    id: headquarters
                    anchors.fill: parent
                    source: "company_headquarters.png"
                    fillMode: Image.PreserveAspectFit
                    smooth: true
                    property real fittedW: Math.min(width, height * sourceSize.width / Math.max(1, sourceSize.height))
                    property real fittedH: Math.min(height, width * sourceSize.height / Math.max(1, sourceSize.width))
                    property real offsetX: (width - fittedW) / 2
                    property real offsetY: (height - fittedH) / 2
                    Repeater {
                        model: companyPage.offices
                        delegate: Item {
                            required property var modelData
                            required property int index
                            x: headquarters.offsetX + headquarters.fittedW * modelData.x
                            y: headquarters.offsetY + headquarters.fittedH * modelData.y
                            width: headquarters.fittedW * modelData.w
                            height: headquarters.fittedH * modelData.h
                            Rectangle {
                                anchors.fill: parent; radius: 5
                                color: companyPage.officeState(modelData.agent) === "working" ? "#4400D9FF" : (hit.containsMouse || companyPage.selectedOffice === index ? "#3300D9FF" : "transparent")
                                border.width: companyPage.officeState(modelData.agent) === "working" || hit.containsMouse || companyPage.selectedOffice === index ? 2 : 0
                                border.color: companyPage.stateColor(companyPage.officeState(modelData.agent))
                            }
                            MouseArea {
                                id: hit; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                                onClicked: companyPage.selectedOffice = index
                            }
                        }
                    }
                }
                Rectangle {
                    anchors.left: parent.left; anchors.top: parent.top; anchors.margins: 10
                    color: "#D002111D"; border.color: "#17617D"; radius: 3
                    width: hint.implicitWidth + 18; height: 25
                    Text { id: hint; anchors.centerIn: parent; text: "●  CLICCA SU UN UFFICIO"; color: "#79E9FF"; font.pixelSize: 9; font.bold: true }
                }
            }
            Rectangle {
                Layout.preferredWidth: Math.min(224, companyPage.width * 0.25)
                Layout.fillHeight: true; color: "#04131E"; border.color: "#15516A"; radius: 5
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 10; spacing: 6
                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "AGENTI"; color: "#61DCFF"; font.bold: true; font.pixelSize: 12 }
                        Item { Layout.fillWidth: true }
                        Text { text: companyPage.agents.length + " AGENTI"; color: "#7EA1AF"; font.pixelSize: 9 }
                    }
                    Rectangle { Layout.fillWidth: true; height: 1; color: "#16516A" }
                    Repeater {
                        model: companyPage.agents
                        delegate: Rectangle {
                            required property var modelData
                            Layout.fillWidth: true; Layout.preferredHeight: 35
                            color: "#061C2B"; radius: 3
                            RowLayout {
                                anchors.fill: parent; anchors.leftMargin: 7; anchors.rightMargin: 6; spacing: 6
                                Rectangle { width: 7; height: 7; radius: 4; color: companyPage.stateColor(companyPage.agentStates[modelData.id] || "idle") }
                                Text { text: modelData.name; Layout.fillWidth: true; elide: Text.ElideRight; color: "#D8F0FA"; font.pixelSize: 10 }
                            }
                        }
                    }
                    Item { Layout.fillHeight: true }
                    Rectangle { Layout.fillWidth: true; height: 1; color: "#16516A" }
                    Text { text: "STATO AGENTI"; color: "#67D8F5"; font.bold: true; font.pixelSize: 10 }
                    Text { text: companyPage.missionBusy ? "MISSIONE IN ESECUZIONE" : "COLLEGATI AL BACKEND"; color: "#D6AD62"; font.pixelSize: 9; wrapMode: Text.Wrap; Layout.fillWidth: true }
                    Rectangle { Layout.fillWidth: true; height: 1; color: "#16516A" }
                    Text { text: "UFFICIO SELEZIONATO"; color: "#67D8F5"; font.bold: true; font.pixelSize: 10 }
                    Text {
                        text: companyPage.selectedOffice < 0 ? "Seleziona una stanza sulla mappa" : companyPage.offices[companyPage.selectedOffice].name
                        color: "white"; font.bold: true; font.pixelSize: 11; wrapMode: Text.Wrap; Layout.fillWidth: true
                    }
                    Text {
                        text: companyPage.selectedOffice < 0 ? "" : companyPage.offices[companyPage.selectedOffice].role + "\nResponsabile: " + companyPage.offices[companyPage.selectedOffice].agent
                        color: "#8DAFBD"; font.pixelSize: 10; wrapMode: Text.Wrap; Layout.fillWidth: true
                    }
                    Button {
                        Layout.fillWidth: true; text: "CHIUDI DETTAGLI"; enabled: companyPage.selectedOffice >= 0
                        onClicked: companyPage.selectedOffice = -1
                    }
                }
            }
        }
        Rectangle {
            Layout.fillWidth: true; Layout.preferredHeight: 63; color: "#041421"; radius: 5; border.color: "#14516C"
            RowLayout {
                anchors.fill: parent; anchors.margins: 10; spacing: 10
                ColumnLayout {
                    Layout.fillWidth: true; spacing: 4
                    Text { text: "ATTIVITÀ RECENTI"; color: "#64DFFF"; font.bold: true; font.pixelSize: 10 }
                    Text { text: companyPage.lastActivity; elide: Text.ElideRight; color: "#8AABBA"; font.pixelSize: 10 }
                }
                Rectangle { width: 1; Layout.fillHeight: true; color: "#15516A" }
                ColumnLayout {
                    Layout.fillWidth: true; spacing: 4
                    Text { text: "FLUSSO DI LAVORO"; color: "#64DFFF"; font.bold: true; font.pixelSize: 10 }
                    Text { text: "Idea  →  Piano  →  Sviluppo  →  Test  →  Completato"; color: "#B6D9E7"; font.pixelSize: 10 }
                }
                Rectangle { width: 1; Layout.fillHeight: true; color: "#15516A" }
                ColumnLayout {
                    Layout.fillWidth: true; spacing: 4
                    Text { text: "RISORSE SISTEMA"; color: "#64DFFF"; font.bold: true; font.pixelSize: 10 }
                    Text { text: companyPage.agents.length + " agenti registrati"; color: "#8AABBA"; font.pixelSize: 10 }
                }
            }
        }
    }
    // MISSION CONTROL: solo overlay della pagina COMPANY; la mappa rimane intatta.
    Rectangle {
        id: missionOverlay
        anchors.fill: parent
        visible: companyPage.missionPanelOpen
        z: 100
        color: "#DD010812"
        MouseArea { anchors.fill: parent; onClicked: companyPage.missionPanelOpen = false }

        Rectangle {
            id: missionSurface
            anchors.centerIn: parent
            width: Math.min(parent.width - 28, 930)
            height: Math.min(parent.height - 24, 640)
            radius: 12
            color: "#061521"
            border.color: "#23718A"
            border.width: 1
            MouseArea { anchors.fill: parent; onClicked: {} }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 12

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12
                    Rectangle { width: 39; height: 39; radius: 9; color: "#102C3D"; border.color: "#25718B"
                        Text { anchors.centerIn: parent; text: "◈"; font.pixelSize: 25; color: "#68E7FF" }
                    }
                    ColumnLayout { spacing: 2
                        Text { text: "MISSION CONTROL"; font.pixelSize: 21; font.bold: true; font.letterSpacing: 1.8; color: "#E1F9FF" }
                        Text { text: "J.A.R.V.I.S.  /  AI COMPANY OPERATIONS"; font.pixelSize: 9; font.letterSpacing: 1.4; color: "#69AFC2" }
                    }
                    Item { Layout.fillWidth: true }
                    Rectangle { width: 8; height: 8; radius: 4; color: companyPage.missionBusy ? "#00D9FF" : "#00E18A" }
                    Text { text: companyPage.missionBusy ? "OPERATIVA" : "PRONTA"; color: "#A6D9E8"; font.pixelSize: 10; font.bold: true }
                    Rectangle { width: 31; height: 31; radius: 7; color: closeArea.containsMouse ? "#24465A" : "#0C2635"; border.color: "#28566A"
                        Text { anchors.centerIn: parent; text: "×"; color: "#D4F4FF"; font.pixelSize: 23 }
                        MouseArea { id: closeArea; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: companyPage.missionPanelOpen = false }
                    }
                }
                Rectangle { Layout.fillWidth: true; height: 1; color: "#1B4558" }

                RowLayout { Layout.fillWidth: true; spacing: 6
                    Repeater { model: ["NUOVA MISSIONE", "ATTIVITÀ LIVE", "RISULTATO"]
                        delegate: Rectangle {
                            required property string modelData
                            required property int index
                            Layout.preferredWidth: 142; Layout.preferredHeight: 33
                            radius: 6
                            color: companyPage.missionTab === index ? "#12445A" : "#0A202D"
                            border.color: companyPage.missionTab === index ? "#39B6D8" : "#183E50"
                            Text { anchors.centerIn: parent; text: modelData; color: companyPage.missionTab === index ? "#DDF9FF" : "#7FAEBE"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 0.5 }
                            MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: companyPage.missionTab = index }
                        }
                    }
                    Item { Layout.fillWidth: true }
                    Text { text: companyPage.missionBusy ? "● MISSIONE IN CORSO" : "● SISTEMA DISPONIBILE"; font.pixelSize: 9; color: companyPage.missionBusy ? "#72E3F9" : "#76D9B5" }
                }

                // NEW MISSION
                ColumnLayout { Layout.fillWidth: true; Layout.fillHeight: true; spacing: 12; visible: companyPage.missionTab === 0
                    Text { text: "AFFIDA UN OBIETTIVO ALLA TUA AZIENDA"; color: "#A5DAEB"; font.pixelSize: 11; font.bold: true; font.letterSpacing: 1 }
                    Text { text: "Descrivi il risultato che vuoi ottenere. J.A.R.V.I.S. sceglierà automaticamente se usare un agente o un workflow multi-agent."; color: "#8FB4C2"; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                    Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; radius: 9; color: "#091D2A"; border.color: missionInput.activeFocus ? "#3AAFD0" : "#245166"; border.width: 1
                        ScrollView { anchors.fill: parent; anchors.margins: 10; clip: true
                            TextArea { id: missionInput; placeholderText: "Esempio: Realizza un'applicazione Python completa, organizzando sviluppo, interfaccia e test..."; placeholderTextColor: "#5E8496"; color: "#E6F8FF"; font.pixelSize: 13; wrapMode: TextArea.Wrap; background: null; selectByMouse: true }
                        }
                    }
                    RowLayout { Layout.fillWidth: true
                        Text { text: "◈  ORCHESTRAZIONE AUTOMATICA"; color: "#72BBD2"; font.pixelSize: 10 }
                        Item { Layout.fillWidth: true }
                        Rectangle { Layout.preferredWidth: 175; Layout.preferredHeight: 39; radius: 7; color: missionInput.text.trim().length && !companyPage.missionBusy ? "#00A8D1" : "#17445A"
                            Text { anchors.centerIn: parent; text: companyPage.missionBusy ? "MISSIONE IN CORSO" : "AVVIA MISSIONE  →"; color: "#F1FDFF"; font.pixelSize: 11; font.bold: true }
                            MouseArea { anchors.fill: parent; enabled: missionInput.text.trim().length > 0 && !companyPage.missionBusy; cursorShape: Qt.PointingHandCursor; onClicked: companyPage.launchMission() }
                        }
                    }
                }

                // LIVE ACTIVITY
                ColumnLayout { Layout.fillWidth: true; Layout.fillHeight: true; spacing: 10; visible: companyPage.missionTab === 1
                    Text { text: companyPage.missionTitle.length ? companyPage.missionTitle : "NESSUNA MISSIONE AVVIATA"; Layout.fillWidth: true; elide: Text.ElideRight; color: "#E4F8FF"; font.pixelSize: 13; font.bold: true }
                    RowLayout { Layout.fillWidth: true; spacing: 8
                        Repeater { model: [{label:"AGENTI REGISTRATI", value: String(companyPage.agents.length)}, {label:"STEP COMPLETATI", value: companyPage.finishedSteps + " / " + (companyPage.totalSteps || "—")}, {label:"STATO", value: companyPage.missionBusy ? "WORKING" : (companyPage.lastResult ? "FINISHED" : "IDLE")}]
                            delegate: Rectangle { required property var modelData; Layout.fillWidth: true; Layout.preferredHeight: 60; radius: 7; color: "#0B2635"; border.color: "#21516A"
                                ColumnLayout { anchors.centerIn: parent; spacing: 4
                                    Text { text: modelData.label; color: "#78AABB"; font.pixelSize: 9; font.bold: true }
                                    Text { text: modelData.value; color: "#C9F6FF"; font.pixelSize: 17; font.bold: true }
                                }
                            }
                        }
                    }
                    Text { text: "TIMELINE OPERATIVA"; color: "#6ADAF5"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 1 }
                    Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; radius: 8; color: "#081B28"; border.color: "#1A4255"
                        ScrollView { anchors.fill: parent; anchors.margins: 9; clip: true
                            ListView { id: missionEvents; model: companyPage.missionTimeline; spacing: 7; clip: true
                                onCountChanged: Qt.callLater(function() { if (missionEvents.count) missionEvents.positionViewAtEnd() })
                                delegate: Rectangle { required property var modelData; width: missionEvents.width - 6; height: eventBody.implicitHeight + 19; radius: 6; color: "#0C2939"
                                    RowLayout { id: eventBody; anchors.left: parent.left; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; anchors.margins: 10; spacing: 9
                                        Rectangle { width: 7; height: 7; radius: 4; color: modelData.kind === "error" ? "#FF7086" : modelData.kind === "working" ? "#00D9FF" : "#00DF9C" }
                                        ColumnLayout { Layout.fillWidth: true; spacing: 3
                                            Text { text: modelData.agent; color: "#D8F4FF"; font.pixelSize: 11; font.bold: true }
                                            Text { text: modelData.detail; color: "#8FB8C8"; font.pixelSize: 10; wrapMode: Text.WordWrap; Layout.fillWidth: true; maximumLineCount: 3; elide: Text.ElideRight }
                                        }
                                        Text { text: modelData.kind === "working" ? "WORKING" : modelData.kind === "error" ? "ERROR" : "DONE"; color: modelData.kind === "error" ? "#FF7086" : modelData.kind === "working" ? "#5CE4FF" : "#72E5B6"; font.pixelSize: 9; font.bold: true }
                                    }
                                }
                            }
                        }
                        Text { anchors.centerIn: parent; visible: companyPage.missionTimeline.length === 0; text: "Le attività degli agenti appariranno qui"; color: "#7096A8"; font.pixelSize: 12 }
                    }
                }

                // RESULTS
                ColumnLayout { Layout.fillWidth: true; Layout.fillHeight: true; spacing: 9; visible: companyPage.missionTab === 2
                    RowLayout { Layout.fillWidth: true
                        Text { text: "REPORT DELLA MISSIONE"; color: "#6ADAF5"; font.pixelSize: 11; font.bold: true; font.letterSpacing: 1 }
                        Item { Layout.fillWidth: true }
                        Text { text: companyPage.missionBusy ? "IN ELABORAZIONE" : (companyPage.lastResult ? (companyPage.lastMissionSuccess ? "COMPLETATA" : "CON ERRORI") : "IN ATTESA"); color: companyPage.missionBusy ? "#6ADAF5" : companyPage.lastMissionSuccess ? "#7AE6B8" : "#FF9DAB"; font.pixelSize: 10; font.bold: true }
                    }
                    Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; radius: 8; color: "#081B28"; border.color: "#1D5065"
                        ScrollView { anchors.fill: parent; anchors.margins: 10; clip: true
                            TextArea { text: companyPage.lastResult || "Il risultato sarà disponibile al termine della missione."; readOnly: true; color: "#D5F0FA"; font.family: "Consolas"; font.pixelSize: 11; wrapMode: TextArea.Wrap; selectByMouse: true; background: null }
                        }
                    }
                    RowLayout { Layout.fillWidth: true
                        Text { text: companyPage.deliverySummary || "In attesa della consegna dei file Python"; color: "#6E9CAD"; font.pixelSize: 9; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                        Item { Layout.fillWidth: true }
                        Rectangle { width: 125; height: 32; radius: 6; color: "#114057"; border.color: "#287A97"
                            Text { anchors.centerIn: parent; text: "COPIA REPORT"; font.pixelSize: 10; font.bold: true; color: "#D8F5FF" }
                            MouseArea { anchors.fill: parent; enabled: !!companyPage.lastResult; cursorShape: Qt.PointingHandCursor; onClicked: { resultCopy.selectAll(); resultCopy.copy(); resultCopy.deselect() } }
                        }
                    }
                    TextEdit { id: resultCopy; text: companyPage.lastResult; visible: false }
                }
            }
        }
    }

}
