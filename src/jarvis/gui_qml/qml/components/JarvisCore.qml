import QtQuick

Item {
    id: root

    property string state: "STARTING"

    property color accentColor:
        "#00CFFF"

    property real audioLevel: 0.0

    property real reactiveLevel:
        Math.max(
            0,
            Math.min(
                audioLevel,
                1
            )
        )

    property real stateActivity: {
        if (state === "THINKING")
            return 1.7

        if (state === "LISTENING")
            return 0.8

        if (state === "SPEAKING")
            return 0.8

        if (state === "STARTING")
            return 0.7

        if (state === "ERROR")
            return 0.25

        return 0.32
    }

    property real activity:
        stateActivity
        + reactiveLevel * 2.2

    property real pulseAmount: 0

    width: 420
    height: 420


    SequentialAnimation
    on pulseAmount {

        loops:
            Animation.Infinite

        NumberAnimation {
            from: 0
            to: 1

            duration:
                Math.max(
                    180,
                    1400
                    / root.activity
                )

            easing.type:
                Easing.InOutSine
        }

        NumberAnimation {
            from: 1
            to: 0

            duration:
                Math.max(
                    180,
                    1400
                    / root.activity
                )

            easing.type:
                Easing.InOutSine
        }
    }


    Canvas {
        id: aura

        anchors.fill: parent

        onPaint: {

            var ctx =
                getContext("2d")

            ctx.reset()

            var cx =
                width / 2

            var cy =
                height / 2

            var base =
                Math.min(
                    width,
                    height
                )

            var radius =
                base
                * (
                    0.30
                    + root.reactiveLevel
                    * 0.055
                    + root.pulseAmount
                    * 0.008
                )

            var gradient =
                ctx.createRadialGradient(
                    cx,
                    cy,
                    0,
                    cx,
                    cy,
                    radius * 1.7
                )

            gradient.addColorStop(
                0,
                Qt.rgba(
                    root.accentColor.r,
                    root.accentColor.g,
                    root.accentColor.b,
                    0.22
                    + root.reactiveLevel
                    * 0.18
                )
            )

            gradient.addColorStop(
                0.38,
                Qt.rgba(
                    root.accentColor.r,
                    root.accentColor.g,
                    root.accentColor.b,
                    0.08
                )
            )

            gradient.addColorStop(
                1,
                "transparent"
            )

            ctx.fillStyle =
                gradient

            ctx.beginPath()

            ctx.arc(
                cx,
                cy,
                radius * 1.7,
                0,
                Math.PI * 2
            )

            ctx.fill()
        }


        Connections {
            target: root

            function onAudioLevelChanged() {
                aura.requestPaint()
            }

            function onPulseAmountChanged() {
                aura.requestPaint()
            }

            function onAccentColorChanged() {
                aura.requestPaint()
            }
        }
    }


    Item {
        id: outerScanner

        anchors.fill: parent


        RotationAnimator on rotation {
            from: 0
            to: 360

            duration:
                Math.max(
                    2200,
                    26000
                    / root.activity
                )

            loops:
                Animation.Infinite
        }


        Repeater {
            model: 120


            Rectangle {
                required property int index

                width:
                    index % 10 === 0
                    ? 18
                    : index % 5 === 0
                      ? 10
                      : 4

                height:
                    index % 10 === 0
                    ? 2
                    : 1

                radius: 1

                color:
                    index % 10 === 0
                    ? root.accentColor
                    : "#4A84A0"

                opacity:
                    index % 10 === 0
                    ? 0.95
                    : 0.20
                    + root.reactiveLevel
                    * 0.30

                x:
                    outerScanner.width / 2
                    + Math.cos(
                        index
                        * Math.PI
                        * 2
                        / 120
                    )
                    * outerScanner.width
                    * (
                        0.445
                        + root.reactiveLevel
                        * 0.012
                    )
                    - width / 2

                y:
                    outerScanner.height / 2
                    + Math.sin(
                        index
                        * Math.PI
                        * 2
                        / 120
                    )
                    * outerScanner.height
                    * (
                        0.445
                        + root.reactiveLevel
                        * 0.012
                    )
                    - height / 2

                rotation:
                    index
                    * 360
                    / 120
                    + 90
            }
        }
    }


    Item {
        id: innerRing

        anchors.centerIn: parent

        width:
            parent.width
            * (
                0.68
                + root.reactiveLevel
                * 0.035
            )

        height: width


        RotationAnimator on rotation {
            from: 360
            to: 0

            duration:
                Math.max(
                    1700,
                    12000
                    / root.activity
                )

            loops:
                Animation.Infinite
        }


        Repeater {
            model: 24


            Rectangle {
                required property int index

                width:
                    index % 4 === 0
                    ? 30
                    : 12

                height:
                    index % 4 === 0
                    ? 2
                    : 1

                radius: 1

                color:
                    root.accentColor

                opacity:
                    index % 4 === 0
                    ? 0.90
                    : 0.18

                x:
                    innerRing.width / 2
                    + Math.cos(
                        index
                        * Math.PI
                        * 2
                        / 24
                    )
                    * innerRing.width
                    * 0.46
                    - width / 2

                y:
                    innerRing.height / 2
                    + Math.sin(
                        index
                        * Math.PI
                        * 2
                        / 24
                    )
                    * innerRing.height
                    * 0.46
                    - height / 2

                rotation:
                    index
                    * 15
                    + 90
            }
        }
    }


    Rectangle {
        anchors.centerIn: parent

        width:
            parent.width
            * (
                0.47
                + root.reactiveLevel
                * 0.025
            )

        height: width

        radius:
            width / 2

        color: "#030B12"

        border.width: 1

        border.color:
            Qt.rgba(
                root.accentColor.r,
                root.accentColor.g,
                root.accentColor.b,
                0.58
            )

        Behavior on width {
            NumberAnimation {
                duration: 70
            }
        }
    }


    Rectangle {
        anchors.centerIn: parent

        width:
            58
            + root.reactiveLevel
            * 38

        height: width

        radius:
            width / 2

        color:
            Qt.rgba(
                root.accentColor.r,
                root.accentColor.g,
                root.accentColor.b,
                0.16
                + root.reactiveLevel
                * 0.18
            )

        border.width:
            1
            + root.reactiveLevel
            * 2

        border.color:
            root.accentColor

        Behavior on width {
            NumberAnimation {
                duration: 65
            }
        }
    }


    Rectangle {
        anchors.centerIn: parent

        width:
            16
            + root.reactiveLevel
            * 12

        height: width

        radius:
            width / 2

        color: "#EEFCFF"

        opacity:
            0.82
            + root.reactiveLevel
            * 0.18

        Behavior on width {
            NumberAnimation {
                duration: 50
            }
        }
    }


    Rectangle {
        anchors.centerIn: parent

        width:
            parent.width * 0.45

        height: 1

        color:
            Qt.rgba(
                root.accentColor.r,
                root.accentColor.g,
                root.accentColor.b,
                0.12
                + root.reactiveLevel
                * 0.26
            )
    }


    Rectangle {
        anchors.centerIn: parent

        width: 1

        height:
            parent.height * 0.45

        color:
            Qt.rgba(
                root.accentColor.r,
                root.accentColor.g,
                root.accentColor.b,
                0.12
                + root.reactiveLevel
                * 0.26
            )
    }


    Column {
        anchors.horizontalCenter:
            parent.horizontalCenter

        anchors.top:
            parent.verticalCenter

        anchors.topMargin: 76

        spacing: 7


        Text {
            anchors.horizontalCenter:
                parent.horizontalCenter

            text:
                "J.A.R.V.I.S."

            color: "#E9FAFF"

            font.pixelSize: 12

            font.weight:
                Font.DemiBold

            font.letterSpacing: 5
        }


        Text {
            anchors.horizontalCenter:
                parent.horizontalCenter

            text:
                root.state

            color:
                root.accentColor

            font.pixelSize: 9

            font.weight:
                Font.Bold

            font.letterSpacing: 4
        }


        Text {
            anchors.horizontalCenter:
                parent.horizontalCenter

            text:
                "AUDIO // "
                + Math.round(
                    root.reactiveLevel
                    * 100
                )
                + "%"

            color: "#426D81"

            font.pixelSize: 7

            font.letterSpacing: 2
        }
    }
}