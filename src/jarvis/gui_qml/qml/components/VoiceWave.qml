import QtQuick

Item {
    id: root

    property string state: "READY"

    property color accentColor:
        "#00CFFF"

    property real audioLevel: 0.0

    property real visualLevel:
        Math.max(
            0,
            Math.min(
                1,
                audioLevel
            )
        )

    height: 58


    Row {
        anchors.centerIn: parent

        spacing: 3

        Repeater {
            model: 35

            Rectangle {
                required property int index

                width: 3

                radius: 2

                anchors.verticalCenter:
                    parent.verticalCenter

                property real distance:
                    Math.abs(
                        index - 17
                    ) / 17

                property real wave:
                    Math.abs(
                        Math.sin(
                            index * 0.71
                            + phase.value
                        )
                    )

                property real localEnergy:
                    (
                        0.15
                        + wave * 0.85
                    )
                    * (
                        1.0
                        - distance * 0.30
                    )

                height:
                    3
                    + 47
                    * root.visualLevel
                    * localEnergy

                color:
                    root.accentColor

                opacity:
                    0.20
                    + root.visualLevel
                    * 0.80

                Behavior on height {
                    NumberAnimation {
                        duration: 55
                    }
                }

                Behavior on opacity {
                    NumberAnimation {
                        duration: 90
                    }
                }
            }
        }
    }


    QtObject {
        id: phase

        property real value: 0

        NumberAnimation on value {
            from: 0
            to: Math.PI * 12

            duration: 2600

            loops: Animation.Infinite
        }
    }


    Rectangle {
        anchors.horizontalCenter:
            parent.horizontalCenter

        anchors.bottom: parent.bottom

        width:
            parent.width
            * root.visualLevel

        height: 1

        color:
            root.accentColor

        opacity:
            root.visualLevel

        Behavior on width {
            NumberAnimation {
                duration: 80
            }
        }
    }
}