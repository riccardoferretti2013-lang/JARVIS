import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// COMPANY 09 only. All agent/task figures are DEMO, not backend status.
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
    property var agents: ["J.A.R.V.I.S.","Project Manager","Backend Architect","Frontend Developer","QA Engineer","Automation Specialist","Memory Manager","Research Analyst"]

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
                Text { text: "COMPANY // DESIGN PREVIEW"; color: "#8CB8C8"; font.pixelSize: 9 }
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
                                color: hit.containsMouse || companyPage.selectedOffice === index ? "#3300D9FF" : "transparent"
                                border.width: hit.containsMouse || companyPage.selectedOffice === index ? 2 : 0
                                border.color: "#00D9FF"
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
                        Text { text: "8 RUOLI"; color: "#7EA1AF"; font.pixelSize: 9 }
                    }
                    Rectangle { Layout.fillWidth: true; height: 1; color: "#16516A" }
                    Repeater {
                        model: companyPage.agents
                        delegate: Rectangle {
                            required property string modelData
                            Layout.fillWidth: true; Layout.preferredHeight: 35
                            color: "#061C2B"; radius: 3
                            RowLayout {
                                anchors.fill: parent; anchors.leftMargin: 7; anchors.rightMargin: 6; spacing: 6
                                Rectangle { width: 7; height: 7; radius: 4; color: "#D9A544" }
                                Text { text: modelData; Layout.fillWidth: true; elide: Text.ElideRight; color: "#D8F0FA"; font.pixelSize: 10 }
                            }
                        }
                    }
                    Item { Layout.fillHeight: true }
                    Rectangle { Layout.fillWidth: true; height: 1; color: "#16516A" }
                    Text { text: "STATO AGENTI"; color: "#67D8F5"; font.bold: true; font.pixelSize: 10 }
                    Text { text: "DEMO — NON COLLEGATI"; color: "#D6AD62"; font.pixelSize: 9; wrapMode: Text.Wrap; Layout.fillWidth: true }
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
                    Text { text: "In attesa di collegamento ai task reali"; color: "#8AABBA"; font.pixelSize: 10 }
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
                    Text { text: "Dati reali: integrazione successiva"; color: "#8AABBA"; font.pixelSize: 10 }
                }
            }
        }
    }
}
