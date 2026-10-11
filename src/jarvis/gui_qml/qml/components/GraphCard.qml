import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root

    property string title: "CPU"
    property string value: "0%"
    property var history: []
    property color accentColor: "#00CFFF"
    property real maxValue: 100

    radius: 7

    color: "#B8040D14"

    border.width: 1
    border.color: "#263A5360"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10

        spacing: 4

        RowLayout {
            Layout.fillWidth: true

            Text {
                text: root.title

                color: "#527E92"

                font.pixelSize: 7
                font.letterSpacing: 2
            }

            Item {
                Layout.fillWidth: true
            }

            Text {
                text: root.value

                color: root.accentColor

                font.pixelSize: 13
                font.weight: Font.Medium
            }
        }

        LiveGraph {
            Layout.fillWidth: true
            Layout.fillHeight: true

            values: root.history
            lineColor: root.accentColor
            maxValue: root.maxValue
        }
    }
}