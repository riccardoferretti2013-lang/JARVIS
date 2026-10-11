import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


Item {
    id: visionPage

    property string frameSource: ""
    property bool cameraOnline: false
    property int handsCount: 0
    property string gestureState: "STARTING"
    property string lastCommand: "NONE"
    property string errorMessage: ""

    property color accentColor: "#00CFFF"


    RowLayout {
        anchors.fill: parent

        spacing: 12


        // ========================================================
        // LEFT - LIVE CAMERA
        // ========================================================

        Rectangle {
            id: videoPanel

            Layout.fillWidth: true
            Layout.fillHeight: true

            Layout.minimumWidth: 600

            radius: 8

            color: "#02090E"

            border.width: 1

            border.color:
                visionPage.cameraOnline
                ? "#00CFFF"
                : "#6A2635"

            clip: true


            // ====================================================
            // VIDEO FEED
            // ====================================================

            Image {
                id: cameraImage

                anchors.fill: parent

                anchors.margins: 8

                source:
                    visionPage.frameSource

                fillMode:
                    Image.PreserveAspectFit

                cache: false

                asynchronous: false

                smooth: true

                visible:
                    visionPage.frameSource.length > 0
            }


            // ====================================================
            // EMPTY VIDEO MESSAGE
            // ====================================================

            Rectangle {
                anchors.fill: parent

                anchors.margins: 8

                visible:
                    visionPage.frameSource.length === 0

                color: "#030B10"


                Column {
                    anchors.centerIn: parent

                    spacing: 12


                    Text {
                        anchors.horizontalCenter:
                            parent.horizontalCenter

                        text:
                            visionPage.cameraOnline
                            ? "CAMERA ONLINE"
                            : "CAMERA OFFLINE"

                        color:
                            visionPage.cameraOnline
                            ? "#00E59B"
                            : "#FF4D6D"

                        font.pixelSize: 18

                        font.letterSpacing: 3
                    }


                    Text {
                        anchors.horizontalCenter:
                            parent.horizontalCenter

                        text:
                            visionPage.cameraOnline
                            ? "WAITING FOR VIDEO FRAME..."
                            : visionPage.errorMessage

                        color: "#52798B"

                        font.pixelSize: 10
                    }
                }
            }


            // ====================================================
            // TOP LEFT CAMERA STATUS
            // ====================================================

            Rectangle {
                anchors.left: parent.left
                anchors.top: parent.top

                anchors.leftMargin: 18
                anchors.topMargin: 18

                width:
                    liveText.implicitWidth + 24

                height: 30

                radius: 5

                color: "#DD051118"

                border.width: 1

                border.color:
                    visionPage.cameraOnline
                    ? "#00E59B"
                    : "#FF4D6D"


                Text {
                    id: liveText

                    anchors.centerIn: parent

                    text:
                        visionPage.cameraOnline
                        ? "● LIVE CAMERA"
                        : "● CAMERA OFFLINE"

                    color:
                        visionPage.cameraOnline
                        ? "#00E59B"
                        : "#FF4D6D"

                    font.pixelSize: 8

                    font.letterSpacing: 1
                }
            }


            // ====================================================
            // TOP RIGHT ENGINE
            // ====================================================

            Rectangle {
                anchors.right: parent.right
                anchors.top: parent.top

                anchors.rightMargin: 18
                anchors.topMargin: 18

                width: 170
                height: 30

                radius: 5

                color: "#DD051118"

                border.width: 1

                border.color: "#244656"


                Text {
                    anchors.centerIn: parent

                    text:
                        "MEDIAPIPE // ACTIVE"

                    color: "#79AABD"

                    font.pixelSize: 7

                    font.letterSpacing: 1
                }
            }


            // ====================================================
            // VIDEO BOTTOM HUD
            // ====================================================

            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom

                anchors.leftMargin: 18
                anchors.rightMargin: 18
                anchors.bottomMargin: 18

                height: 54

                radius: 6

                color: "#DD040D14"

                border.width: 1

                border.color: "#20495A"


                RowLayout {
                    anchors.fill: parent

                    anchors.leftMargin: 16
                    anchors.rightMargin: 16

                    spacing: 12


                    Column {
                        spacing: 3


                        Text {
                            text:
                                "GESTURE"

                            color: "#52798B"

                            font.pixelSize: 6

                            font.letterSpacing: 2
                        }


                        Text {
                            text:
                                visionPage.gestureState

                            color: "#00CFFF"

                            font.pixelSize: 10
                        }
                    }


                    Item {
                        Layout.fillWidth: true
                    }


                    Text {
                        text:
                            "CLAP → WORK MODE"

                        color: "#587F90"

                        font.pixelSize: 8

                        font.letterSpacing: 1
                    }
                }
            }
        }


        // ========================================================
        // RIGHT - VISION DATA
        // ========================================================

        ColumnLayout {
            id: infoColumn

            Layout.minimumWidth: 300
            Layout.maximumWidth: 320
            Layout.preferredWidth: 320

            Layout.fillHeight: true

            spacing: 10


            VisionCard {
                Layout.fillWidth: true

                title:
                    "CAMERA"

                value:
                    visionPage.cameraOnline
                    ? "ONLINE"
                    : "OFFLINE"

                detail:
                    "LIVE WEBCAM FEED"

                accent:
                    visionPage.cameraOnline
                    ? "#00E59B"
                    : "#FF4D6D"
            }


            VisionCard {
                Layout.fillWidth: true

                title:
                    "HANDS DETECTED"

                value:
                    visionPage.handsCount.toString()

                detail:
                    "MEDIAPIPE HAND TRACKING"

                accent:
                    visionPage.handsCount >= 2
                    ? "#00CFFF"
                    : "#FFC857"
            }


            VisionCard {
                Layout.fillWidth: true

                title:
                    "GESTURE"

                value:
                    visionPage.gestureState

                detail:
                    "CLAP RECOGNITION ENGINE"

                accent:
                    visionPage.gestureState === "CLAP DETECTED"
                    ? "#00E59B"
                    : "#8B7CFF"
            }


            VisionCard {
                Layout.fillWidth: true
                Layout.fillHeight: true

                title:
                    "LAST COMMAND"

                value:
                    visionPage.lastCommand

                detail:
                    visionPage.lastCommand === "NONE"
                    ? "WAITING FOR GESTURE"
                    : "COMMAND SENT TO J.A.R.V.I.S."

                accent:
                    "#00CFFF"
            }
        }
    }


    // ============================================================
    // VISION CARD
    // ============================================================

    component VisionCard: Rectangle {
        id: card

        property string title: ""
        property string value: ""
        property string detail: ""

        property color accent: "#00CFFF"

        implicitHeight: 120

        radius: 7

        color: "#AA061019"

        border.width: 1

        border.color:
            Qt.rgba(
                accent.r,
                accent.g,
                accent.b,
                0.35
            )


        Column {
            anchors.fill: parent

            anchors.margins: 14

            spacing: 8


            Text {
                text:
                    card.title

                color: "#52798B"

                font.pixelSize: 7

                font.letterSpacing: 2
            }


            Text {
                width: parent.width

                text:
                    card.value

                color:
                    card.accent

                font.pixelSize: 21

                font.weight:
                    Font.Light

                elide:
                    Text.ElideRight
            }


            Text {
                width: parent.width

                text:
                    card.detail

                color: "#527080"

                wrapMode:
                    Text.Wrap

                font.pixelSize: 8
            }
        }
    }
}