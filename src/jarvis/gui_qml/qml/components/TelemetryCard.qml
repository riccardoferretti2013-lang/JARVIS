import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root

    property string title: "SYSTEM"
    property string code: "SYS"
    property string value: "0%"
    property string description: ""

    property color accentColor:
        "#00CFFF"

    property real level: 0

    height: 88

    radius: 7

    color: "#BA041018"

    border.width: 1
    border.color: "#243B5360"

    ColumnLayout {
        anchors.fill: parent

        anchors.margins: 10

        spacing: 4

        RowLayout {
            Layout.fillWidth: true

            Text {
                text:
                    root.code
                    + " // "
                    + root.title

                color: "#4F8198"

                font.pixelSize: 7
                font.letterSpacing: 1
            }

            Item {
                Layout.fillWidth: true
            }

            Rectangle {
                width: 6
                height: 6

                radius: 3

                color:
                    root.accentColor

                opacity: 0.9
            }
        }

        Text {
            text:
                root.value

            color: "#E3F7FF"

            font.pixelSize: 17
            font.weight: Font.Medium
        }

        Text {
            text:
                root.description

            visible:
                text.length > 0

            color: "#527384"

            font.pixelSize: 7
        }

        Item {
            Layout.fillHeight: true
        }

        Rectangle {
            Layout.fillWidth: true

            height: 3

            radius: 2

            color: "#182731"

            Rectangle {
                width:
                    parent.width
                    * Math.max(
                        0,
                        Math.min(
                            root.level,
                            1
                        )
                    )

                height:
                    parent.height

                radius:
                    parent.radius

                color:
                    root.accentColor

                Behavior on width {
                    NumberAnimation {
                        duration: 500

                        easing.type:
                            Easing.OutCubic
                    }
                }
            }
        }
    }
}