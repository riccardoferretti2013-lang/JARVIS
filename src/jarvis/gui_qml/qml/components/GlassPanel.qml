import QtQuick

Rectangle {
    id: root

    property color accentColor: "#00CFFF"
    property bool highlighted: false
    property real panelOpacity: 0.82

    radius: 10

    color: Qt.rgba(
        0.015,
        0.035,
        0.055,
        panelOpacity
    )

    border.width: 1

    border.color: highlighted
                 ? Qt.rgba(
                       accentColor.r,
                       accentColor.g,
                       accentColor.b,
                       0.55
                   )
                 : "#26354D5E"

    Rectangle {
        anchors.fill: parent
        anchors.margins: 1

        radius: parent.radius - 1

        color: "transparent"

        border.width: 1
        border.color: "#0DFFFFFF"
    }

    Rectangle {
        anchors.left: parent.left
        anchors.top: parent.top

        anchors.leftMargin: 18

        width: Math.min(
            parent.width * 0.28,
            170
        )

        height: 1

        color: accentColor
        opacity: highlighted ? 0.95 : 0.55
    }

    Rectangle {
        anchors.left: parent.left
        anchors.top: parent.top

        width: 18
        height: 1

        color: accentColor
        opacity: 0.85
    }

    Rectangle {
        anchors.left: parent.left
        anchors.top: parent.top

        width: 1
        height: 18

        color: accentColor
        opacity: 0.85
    }

    Rectangle {
        anchors.right: parent.right
        anchors.bottom: parent.bottom

        width: 16
        height: 1

        color: accentColor
        opacity: 0.35
    }

    Rectangle {
        anchors.right: parent.right
        anchors.bottom: parent.bottom

        width: 1
        height: 16

        color: accentColor
        opacity: 0.35
    }
}