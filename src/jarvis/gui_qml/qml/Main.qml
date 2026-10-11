import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "components"


ApplicationWindow {
    id: window

    width: 1540
    height: 920

    minimumWidth: 1250
    minimumHeight: 740

    visible: true

    title: "J.A.R.V.I.S."

    color: "transparent"

    flags:
        Qt.Window
        | Qt.FramelessWindowHint


    // ============================================================
    // GENERAL STATE
    // ============================================================

    property string jarvisState: "STARTING"
    property color jarvisColor: "#00D9FF"

    property int activePage: 0
    property int currentStreamIndex: -1

    property point dragStart:
        Qt.point(0, 0)


    // ============================================================
    // TELEMETRY
    // ============================================================

    property real cpuUsage: 0
    property real ramUsage: 0
    property real diskUsage: 0
    property real networkSpeed: 0
    property real gpuUsage: 0
    property real performance: 0

    property string uptime: "--"

    property var cpuHistory: []
    property var ramHistory: []
    property var gpuHistory: []


    // ============================================================
    // AUDIO
    // ============================================================

    property real inputAudioLevel: 0.0
    property real outputAudioLevel: 0.0

    property real activeAudioLevel:
        Math.max(
            inputAudioLevel,
            outputAudioLevel
        )

    property real visualAudioLevel:
        Math.min(
            1.0,
            activeAudioLevel * 1.25
        )


    // ============================================================
    // BOOT
    // ============================================================

    property bool bootFinished: false
    property bool bootPhaseTwo: false
    property bool bootPhaseThree: false


    // ============================================================
    // MEMORY
    // ============================================================

    property int memoryTotal: 0
    property int semanticMemoryTotal: 0

    property string memoryStatusMessage:
        "MEMORY SERVICE READY"

    property bool memoryStatusSuccess: true
    property bool clearMemoryArmed: false


    // ============================================================
    // VISION
    // ============================================================

    property string visionFrame: ""

    property bool visionCameraOnline:
        false

    property int visionHandsCount:
        0

    property string visionGesture:
        "STARTING"

    property string visionCommand:
        "NONE"

    property string visionError:
        ""


    // ============================================================
    // NAVIGATION
    // ============================================================

    property var navigationItems: [
        {
            "label": "01   CHAT",
            "title": "CONVERSATION",
            "subtitle": "TEXT + VOICE INTERFACE"
        },
        {
            "label": "02   VOICE",
            "title": "VOICE CORE",
            "subtitle": "LIVE AUDIO INTERFACE"
        },
        {
            "label": "03   MEMORY",
            "title": "MEMORY",
            "subtitle": "LONG-TERM MEMORY MATRIX"
        },
        {
            "label": "04   PROJECTS",
            "title": "PROJECTS",
            "subtitle": "ACTIVE WORKSPACES"
        },
        {
            "label": "05   TOOLS",
            "title": "TOOLS",
            "subtitle": "DIRECT SYSTEM COMMANDS"
        },
        {
            "label": "06   SYSTEM",
            "title": "SYSTEM",
            "subtitle": "LIVE TELEMETRY"
        },
        {
            "label": "07   AUTOMATION",
            "title": "AUTOMATION",
            "subtitle": "ROUTINES & EXECUTION"
        },
        {
            "label": "08   VISION",
            "title": "VISION",
            "subtitle": "LIVE CAMERA + GESTURE CONTROL"
        }
    ]


    // ============================================================
    // STARTUP
    // ============================================================

    Component.onCompleted: {

        jarvisBridge.start()

        visionBridge.start()

        bootTimer.start()
    }


    onClosing:
        function(close) {

            close.accepted = false

            window.hide()
        }


    // ============================================================
    // MODELS
    // ============================================================

    ListModel {
        id: chatModel
    }


    ListModel {
        id: memoryModel
    }


    // ============================================================
    // TIMERS
    // ============================================================

    Timer {
        id: bootTimer

        interval: 700
        repeat: false

        onTriggered: {

            window.bootPhaseTwo = true

            bootTimerTwo.start()
        }
    }


    Timer {
        id: bootTimerTwo

        interval: 850
        repeat: false

        onTriggered: {

            window.bootPhaseThree = true

            bootTimerThree.start()
        }
    }


    Timer {
        id: bootTimerThree

        interval: 950
        repeat: false

        onTriggered: {

            window.bootFinished = true
        }
    }


    Timer {
        id: clearMemoryTimer

        interval: 5000
        repeat: false

        onTriggered: {

            window.clearMemoryArmed = false
        }
    }


    Timer {
        id: memoryMessageTimer

        interval: 4500
        repeat: false

        onTriggered: {

            window.memoryStatusMessage =
                "MEMORY SERVICE READY"

            window.memoryStatusSuccess =
                true
        }
    }


    // ============================================================
    // JARVIS BRIDGE
    // ============================================================

    Connections {
        target: jarvisBridge


        function onStateChanged(
            state,
            color
        ) {

            window.jarvisState =
                state

            window.jarvisColor =
                color
        }


        function onAudioLevelChanged(
            source,
            level
        ) {

            var safeLevel =
                Math.max(
                    0,
                    Math.min(
                        1,
                        level
                    )
                )

            if (
                source
                === "input"
            ) {

                window.inputAudioLevel =
                    safeLevel
            }

            else if (
                source
                === "output"
            ) {

                window.outputAudioLevel =
                    safeLevel
            }
        }


        function onTelemetryChanged(
            cpu,
            memory,
            disk,
            network,
            gpu,
            score,
            uptimeText
        ) {

            window.cpuUsage =
                cpu

            window.ramUsage =
                memory

            window.diskUsage =
                disk

            window.networkSpeed =
                network

            window.gpuUsage =
                gpu

            window.performance =
                score

            window.uptime =
                uptimeText


            var cpuArray =
                window.cpuHistory.slice()

            cpuArray.push(
                cpu
            )

            if (
                cpuArray.length
                > 45
            ) {

                cpuArray.shift()
            }

            window.cpuHistory =
                cpuArray


            var ramArray =
                window.ramHistory.slice()

            ramArray.push(
                memory
            )

            if (
                ramArray.length
                > 45
            ) {

                ramArray.shift()
            }

            window.ramHistory =
                ramArray


            var gpuArray =
                window.gpuHistory.slice()

            gpuArray.push(
                gpu
            )

            if (
                gpuArray.length
                > 45
            ) {

                gpuArray.shift()
            }

            window.gpuHistory =
                gpuArray
        }


        function onAssistantMessage(
            message
        ) {

            chatModel.append({
                "role":
                    "J.A.R.V.I.S.",

                "text":
                    message,

                "accent":
                    "#00D9FF"
            })

            if (
                chatView.count
                > 0
            ) {

                chatView.positionViewAtEnd()
            }
        }


        function onStreamStarted() {

            chatModel.append({
                "role":
                    "J.A.R.V.I.S.",

                "text":
                    "",

                "accent":
                    "#00D9FF"
            })

            window.currentStreamIndex =
                chatModel.count - 1

            if (
                chatView.count
                > 0
            ) {

                chatView.positionViewAtEnd()
            }
        }


        function onStreamChunk(
            chunk
        ) {

            if (
                window.currentStreamIndex
                < 0
            ) {

                return
            }

            var previous =
                chatModel
                .get(
                    window.currentStreamIndex
                )
                .text

            chatModel.setProperty(
                window.currentStreamIndex,
                "text",
                previous + chunk
            )

            if (
                chatView.count
                > 0
            ) {

                chatView.positionViewAtEnd()
            }
        }


        function onStreamFinished() {

            window.currentStreamIndex =
                -1
        }


        function onVoiceCommandDetected(
            command
        ) {

            chatModel.append({
                "role":
                    "RICCARDO // VOICE",

                "text":
                    command,

                "accent":
                    "#74A7BD"
            })

            if (
                chatView.count
                > 0
            ) {

                chatView.positionViewAtEnd()
            }
        }


        function onErrorOccurred(
            message
        ) {

            chatModel.append({
                "role":
                    "SYSTEM ERROR",

                "text":
                    message,

                "accent":
                    "#FF4D6D"
            })

            if (
                chatView.count
                > 0
            ) {

                chatView.positionViewAtEnd()
            }
        }


        // ========================================================
        // MEMORY
        // ========================================================

        function onMemoryDataChanged(
            memories,
            totalCount,
            semanticCount
        ) {

            memoryModel.clear()

            window.memoryTotal =
                totalCount

            window.semanticMemoryTotal =
                semanticCount


            for (
                var i = 0;
                i < memories.length;
                i++
            ) {

                var item =
                    memories[i]

                memoryModel.append({
                    "memoryId":
                        item.memoryId,

                    "memoryKey":
                        item.key,

                    "memoryValue":
                        item.value,

                    "memoryType":
                        item.memoryType,

                    "importance":
                        item.importance,

                    "createdAt":
                        item.createdAt,

                    "updatedAt":
                        item.updatedAt
                })
            }
        }


        function onMemoryOperationCompleted(
            operation,
            success,
            message
        ) {

            window.memoryStatusMessage =
                message

            window.memoryStatusSuccess =
                success

            memoryMessageTimer.restart()


            if (
                operation
                === "clear"
                && success
            ) {

                window.clearMemoryArmed =
                    false

                clearMemoryTimer.stop()
            }
        }
    }


    // ============================================================
    // VISION BRIDGE
    // ============================================================

    Connections {
        target: visionBridge


        function onFrameChanged(
            frameSource
        ) {

            window.visionFrame =
                frameSource
        }


        function onStatusChanged(
            cameraOnline,
            handsCount,
            gesture,
            command
        ) {

            window.visionCameraOnline =
                cameraOnline

            window.visionHandsCount =
                handsCount

            window.visionGesture =
                gesture

            window.visionCommand =
                command


            if (
                cameraOnline
            ) {

                window.visionError =
                    ""
            }
        }


        function onErrorOccurred(
            message
        ) {

            window.visionCameraOnline =
                false

            window.visionError =
                message
        }
    }


    // ============================================================
    // BACKGROUND
    // ============================================================

    Rectangle {
        anchors.fill: parent

        radius: 12

        color: "#010407"

        border.width: 1
        border.color: "#354A5B68"

        clip: true


        gradient:
            Gradient {

            GradientStop {
                position: 0
                color: "#071119"
            }

            GradientStop {
                position: 0.45
                color: "#02070C"
            }

            GradientStop {
                position: 1
                color: "#010306"
            }
        }


        // ========================================================
        // GRID
        // ========================================================

        Canvas {
            anchors.fill: parent

            opacity: 0.18


            onPaint: {

                var ctx =
                    getContext("2d")

                ctx.reset()

                ctx.strokeStyle =
                    "#173747"

                ctx.lineWidth =
                    1

                var spacing =
                    46


                for (
                    var x = 0;
                    x < width;
                    x += spacing
                ) {

                    ctx.beginPath()

                    ctx.moveTo(
                        x,
                        0
                    )

                    ctx.lineTo(
                        x,
                        height
                    )

                    ctx.stroke()
                }


                for (
                    var y = 0;
                    y < height;
                    y += spacing
                ) {

                    ctx.beginPath()

                    ctx.moveTo(
                        0,
                        y
                    )

                    ctx.lineTo(
                        width,
                        y
                    )

                    ctx.stroke()
                }
            }
        }


        // ========================================================
        // AMBIENT GLOW
        // ========================================================

        Rectangle {
            id: ambientGlow

            anchors.centerIn:
                parent

            width:
                parent.width
                * (
                    0.72
                    + window.visualAudioLevel
                    * 0.015
                )

            height:
                parent.height
                * (
                    0.78
                    + window.visualAudioLevel
                    * 0.015
                )

            radius:
                Math.max(
                    width,
                    height
                )

            color:
                Qt.rgba(
                    window.jarvisColor.r,
                    window.jarvisColor.g,
                    window.jarvisColor.b,
                    0.025
                    + window.visualAudioLevel
                    * 0.025
                )

            scale:
                0.92
                + (
                    window.jarvisState
                    === "THINKING"
                    ? 0.04
                    : 0
                )
                + window.visualAudioLevel
                * 0.02


            Behavior on scale {

                NumberAnimation {
                    duration: 100

                    easing.type:
                        Easing.OutCubic
                }
            }


            Behavior on width {

                NumberAnimation {
                    duration: 90
                }
            }


            Behavior on height {

                NumberAnimation {
                    duration: 90
                }
            }
        }


        // ========================================================
        // SCAN LINE
        // ========================================================

        Rectangle {
            id: scanLine

            width: parent.width
            height: 1

            color: "#1700D9FF"


            NumberAnimation on y {
                from: 0

                to:
                    window.height

                duration: 10000

                loops:
                    Animation.Infinite
            }
        }


        // ========================================================
        // MAIN INTERFACE
        // ========================================================

        ColumnLayout {
            id: mainInterface

            anchors.fill:
                parent

            anchors.margins:
                12

            spacing:
                10

            opacity:
                window.bootFinished
                ? 1
                : 0

            scale:
                window.bootFinished
                ? 1
                : 0.985


            Behavior on opacity {

                NumberAnimation {
                    duration: 700

                    easing.type:
                        Easing.OutCubic
                }
            }


            Behavior on scale {

                NumberAnimation {
                    duration: 700

                    easing.type:
                        Easing.OutCubic
                }
            }


            // ====================================================
            // TITLE BAR
            // ====================================================

            GlassPanel {
                id: titleBar

                Layout.fillWidth:
                    true

                Layout.preferredHeight:
                    68

                highlighted:
                    true

                accentColor:
                    window.jarvisColor


                MouseArea {
                    anchors.fill:
                        parent

                    acceptedButtons:
                        Qt.LeftButton


                    onPressed:
                        function(mouse) {

                            window.dragStart =
                                Qt.point(
                                    mouse.x,
                                    mouse.y
                                )
                        }


                    onPositionChanged:
                        function(mouse) {

                            if (
                                !(
                                    mouse.buttons
                                    & Qt.LeftButton
                                )
                            ) {

                                return
                            }

                            window.x +=
                                mouse.x
                                - window.dragStart.x

                            window.y +=
                                mouse.y
                                - window.dragStart.y
                        }
                }


                RowLayout {
                    anchors.fill:
                        parent

                    anchors.leftMargin:
                        20

                    anchors.rightMargin:
                        14

                    spacing:
                        17


                    Rectangle {
                        width: 34
                        height: 34

                        radius: 17

                        color: "#0800CFFF"

                        border.width: 1

                        border.color:
                            window.jarvisColor


                        Rectangle {
                            anchors.centerIn:
                                parent

                            width:
                                12
                                + window.visualAudioLevel
                                * 5

                            height:
                                width

                            radius:
                                width / 2

                            color:
                                window.jarvisColor


                            SequentialAnimation on opacity {

                                loops:
                                    Animation.Infinite

                                NumberAnimation {
                                    from: 0.35
                                    to: 1
                                    duration: 800
                                }

                                NumberAnimation {
                                    from: 1
                                    to: 0.35
                                    duration: 800
                                }
                            }
                        }
                    }


                    Column {
                        spacing: 0


                        Text {
                            text:
                                "J . A . R . V . I . S ."

                            color:
                                "#F1FAFF"

                            font.pixelSize:
                                22

                            font.weight:
                                Font.DemiBold

                            font.letterSpacing:
                                5
                        }


                        Text {
                            text:
                                "ADVANCED PERSONAL INTELLIGENCE SYSTEM"

                            color:
                                "#4E7B90"

                            font.pixelSize:
                                7

                            font.letterSpacing:
                                3
                        }
                    }


                    Rectangle {
                        width: 1
                        height: 28

                        color:
                            "#244656"
                    }


                    Text {
                        text:
                            "BUILD 0.1 ALPHA"

                        color:
                            "#4B8DA9"

                        font.pixelSize:
                            8
                    }


                    Item {
                        Layout.fillWidth:
                            true
                    }


                    Text {
                        text:
                            "PAGE // "
                            + window.navigationItems[
                                window.activePage
                            ].title

                        color:
                            "#568AA1"

                        font.pixelSize:
                            8
                    }


                    Text {
                        text:
                            "AUDIO // "
                            + Math.round(
                                window.visualAudioLevel
                                * 100
                            )
                            + "%"

                        color:
                            window.visualAudioLevel
                            > 0.05
                            ? window.jarvisColor
                            : "#426B7D"

                        font.pixelSize:
                            8
                    }


                    Text {
                        text:
                            "● "
                            + window.jarvisState

                        color:
                            window.jarvisColor

                        font.pixelSize:
                            9
                    }


                    Rectangle {
                        width: 1
                        height: 28

                        color:
                            "#244656"
                    }


                    Text {
                        text:
                            "RICCARDO"

                        color:
                            "#AAC8D5"

                        font.pixelSize:
                            9
                    }


                    Rectangle {
                        width: 30
                        height: 30

                        radius: 5

                        color:
                            minimizeMouse.containsMouse
                            ? "#153545"
                            : "transparent"


                        Text {
                            anchors.centerIn:
                                parent

                            text:
                                "—"

                            color:
                                "#8CA9B7"
                        }


                        MouseArea {
                            id: minimizeMouse

                            anchors.fill:
                                parent

                            hoverEnabled:
                                true

                            onClicked: {

                                window.showMinimized()
                            }
                        }
                    }


                    Rectangle {
                        width: 30
                        height: 30

                        radius: 5

                        color:
                            closeMouse.containsMouse
                            ? "#521625"
                            : "transparent"


                        Text {
                            anchors.centerIn:
                                parent

                            text:
                                "×"

                            color:
                                closeMouse.containsMouse
                                ? "#FF7890"
                                : "#8CA9B7"

                            font.pixelSize:
                                16
                        }


                        MouseArea {
                            id: closeMouse

                            anchors.fill:
                                parent

                            hoverEnabled:
                                true

                            onClicked: {

                                window.hide()
                            }
                        }
                    }
                }
            }


            // ====================================================
            // BODY
            // ====================================================

            RowLayout {
                Layout.fillWidth:
                    true

                Layout.fillHeight:
                    true

                spacing:
                    10


                // =================================================
                // SIDEBAR
                // =================================================

                GlassPanel {
                    Layout.preferredWidth:
                        190

                    Layout.fillHeight:
                        true


                    ColumnLayout {
                        anchors.fill:
                            parent

                        anchors.margins:
                            12

                        spacing:
                            6


                        Text {
                            text:
                                "COMMAND MODULES"

                            color:
                                "#416E83"

                            font.pixelSize:
                                7

                            font.letterSpacing:
                                3
                        }


                        Repeater {
                            model:
                                window.navigationItems


                            delegate:
                                Rectangle {

                                required property var modelData
                                required property int index

                                Layout.fillWidth:
                                    true

                                Layout.preferredHeight:
                                    50

                                radius:
                                    5

                                color:
                                    index
                                    === window.activePage
                                    ? "#17009FD9"
                                    : navMouse.containsMouse
                                      ? "#0B0B6688"
                                      : "transparent"

                                border.width:
                                    index
                                    === window.activePage
                                    ? 1
                                    : 0

                                border.color:
                                    "#3700CFFF"


                                Text {
                                    anchors.verticalCenter:
                                        parent.verticalCenter

                                    anchors.left:
                                        parent.left

                                    anchors.leftMargin:
                                        14

                                    text:
                                        modelData.label

                                    color:
                                        index
                                        === window.activePage
                                        ? "#DFFAFF"
                                        : "#7191A0"

                                    font.pixelSize:
                                        9

                                    font.letterSpacing:
                                        1
                                }


                                MouseArea {
                                    id: navMouse

                                    anchors.fill:
                                        parent

                                    hoverEnabled:
                                        true


                                    onClicked: {

                                        window.activePage =
                                            index

                                        if (
                                            index
                                            === 2
                                        ) {

                                            jarvisBridge.loadMemory()
                                        }
                                    }
                                }
                            }
                        }


                        Item {
                            Layout.fillHeight:
                                true
                        }


                        VoiceWave {
                            Layout.fillWidth:
                                true

                            state:
                                window.jarvisState

                            accentColor:
                                window.jarvisColor

                            audioLevel:
                                window.visualAudioLevel
                        }


                        Text {
                            Layout.alignment:
                                Qt.AlignHCenter

                            text: {

                                if (
                                    window.jarvisState
                                    === "LISTENING"
                                ) {

                                    return "LIVE MICROPHONE"
                                }

                                if (
                                    window.jarvisState
                                    === "SPEAKING"
                                ) {

                                    return "LIVE VOICE OUTPUT"
                                }

                                return "VOICE LINK STANDBY"
                            }

                            color:
                                window.jarvisColor

                            font.pixelSize:
                                7

                            font.letterSpacing:
                                2
                        }


                        Text {
                            Layout.alignment:
                                Qt.AlignHCenter

                            text:
                                Math.round(
                                    window.visualAudioLevel
                                    * 100
                                )
                                + "% SIGNAL"

                            color:
                                "#3E6A7D"

                            font.pixelSize:
                                7
                        }


                        Rectangle {
                            Layout.fillWidth:
                                true

                            height:
                                1

                            color:
                                "#173542"
                        }


                        Text {
                            text:
                                "UPTIME // "
                                + window.uptime
                                + "\nLOCAL AI // ACTIVE"
                                + "\nSECURITY // LOCAL"
                                + "\nVISION // "
                                + (
                                    window.visionCameraOnline
                                    ? "ONLINE"
                                    : "OFFLINE"
                                )

                            color:
                                "#35596A"

                            font.pixelSize:
                                7

                            font.letterSpacing:
                                1

                            lineHeight:
                                1.5
                        }
                    }
                }


                // =================================================
                // MAIN PAGE
                // =================================================

                GlassPanel {
                    Layout.fillWidth:
                        true

                    Layout.fillHeight:
                        true

                    highlighted:
                        true

                    accentColor:
                        window.jarvisColor


                    ColumnLayout {
                        anchors.fill:
                            parent

                        anchors.margins:
                            14

                        spacing:
                            10


                        // =========================================
                        // PAGE HEADER
                        // =========================================

                        RowLayout {
                            Layout.fillWidth:
                                true


                            Column {
                                spacing:
                                    1


                                Text {
                                    text:
                                        window.navigationItems[
                                            window.activePage
                                        ].title

                                    color:
                                        "#E8F8FF"

                                    font.pixelSize:
                                        15

                                    font.weight:
                                        Font.DemiBold
                                }


                                Text {
                                    text:
                                        window.navigationItems[
                                            window.activePage
                                        ].subtitle

                                    color:
                                        "#3C6C82"

                                    font.pixelSize:
                                        7

                                    font.letterSpacing:
                                        2
                                }
                            }


                            Item {
                                Layout.fillWidth:
                                    true
                            }


                            Text {
                                visible:
                                    window.activePage
                                    === 7

                                text:
                                    "● VISION "
                                    + (
                                        window.visionCameraOnline
                                        ? "ONLINE"
                                        : "OFFLINE"
                                    )

                                color:
                                    window.visionCameraOnline
                                    ? "#00E59B"
                                    : "#FF4D6D"

                                font.pixelSize:
                                    8
                            }


                            Text {
                                visible:
                                    window.activePage
                                    !== 7

                                text:
                                    "● "
                                    + window.jarvisState

                                color:
                                    window.jarvisColor

                                font.pixelSize:
                                    8
                            }
                        }


                        Rectangle {
                            Layout.fillWidth:
                                true

                            height:
                                1

                            color:
                                "#173744"
                        }


                        // =========================================
                        // PAGE STACK
                        // =========================================

                        StackLayout {
                            id: pageStack

                            Layout.fillWidth:
                                true

                            Layout.fillHeight:
                                true

                            currentIndex:
                                window.activePage


                            // =====================================
                            // PAGE 0 - CHAT
                            // =====================================

                            Item {

                                ColumnLayout {
                                    anchors.fill:
                                        parent

                                    spacing:
                                        9


                                    ListView {
                                        id: chatView

                                        Layout.fillWidth:
                                            true

                                        Layout.fillHeight:
                                            true

                                        clip:
                                            true

                                        spacing:
                                            10

                                        model:
                                            chatModel


                                        delegate:
                                            Rectangle {

                                            required property string role
                                            required property string text
                                            required property string accent

                                            width:
                                                chatView.width
                                                * 0.94

                                            height:
                                                messageColumn
                                                .implicitHeight
                                                + 24

                                            radius:
                                                7

                                            color:
                                                role.indexOf(
                                                    "RICCARDO"
                                                ) >= 0
                                                ? "#A0091A25"
                                                : "#A0031420"

                                            border.width:
                                                1

                                            border.color:
                                                role.indexOf(
                                                    "RICCARDO"
                                                ) >= 0
                                                ? "#234959"
                                                : "#1D536B"


                                            Column {
                                                id: messageColumn

                                                anchors.fill:
                                                    parent

                                                anchors.margins:
                                                    12

                                                spacing:
                                                    6


                                                Text {
                                                    text:
                                                        role

                                                    color:
                                                        accent

                                                    font.pixelSize:
                                                        7

                                                    font.letterSpacing:
                                                        2
                                                }


                                                Text {
                                                    width:
                                                        parent.width

                                                    text:
                                                        parent
                                                        .parent
                                                        .text

                                                    color:
                                                        "#D9EEF6"

                                                    wrapMode:
                                                        Text.Wrap

                                                    font.pixelSize:
                                                        12

                                                    lineHeight:
                                                        1.3
                                                }
                                            }
                                        }
                                    }


                                    Rectangle {
                                        Layout.fillWidth:
                                            true

                                        Layout.preferredHeight:
                                            58

                                        radius:
                                            7

                                        color:
                                            "#DB040D14"

                                        border.width:
                                            1

                                        border.color:
                                            "#214A5D"


                                        RowLayout {
                                            anchors.fill:
                                                parent

                                            anchors.margins:
                                                7

                                            spacing:
                                                7


                                            Rectangle {
                                                Layout.fillWidth:
                                                    true

                                                Layout.fillHeight:
                                                    true

                                                radius:
                                                    5

                                                color:
                                                    "#071019"

                                                border.width:
                                                    1

                                                border.color:
                                                    commandField.activeFocus
                                                    ? window.jarvisColor
                                                    : "#173A4A"


                                                TextInput {
                                                    id: commandField

                                                    anchors.fill:
                                                        parent

                                                    anchors.leftMargin:
                                                        12

                                                    anchors.rightMargin:
                                                        12

                                                    verticalAlignment:
                                                        TextInput.AlignVCenter

                                                    color:
                                                        "#E7F7FF"

                                                    selectionColor:
                                                        "#335E73"

                                                    selectedTextColor:
                                                        "#FFFFFF"

                                                    font.pixelSize:
                                                        12

                                                    clip:
                                                        true

                                                    onAccepted: {

                                                        window.sendCurrentCommand()
                                                    }
                                                }


                                                Text {
                                                    anchors.verticalCenter:
                                                        parent.verticalCenter

                                                    anchors.left:
                                                        parent.left

                                                    anchors.leftMargin:
                                                        12

                                                    visible:
                                                        commandField.text.length
                                                        === 0

                                                    text:
                                                        "Scrivi a J.A.R.V.I.S..."

                                                    color:
                                                        "#416777"

                                                    font.pixelSize:
                                                        11
                                                }
                                            }


                                            ActionButton {
                                                Layout.preferredWidth:
                                                    88

                                                Layout.fillHeight:
                                                    true

                                                label:
                                                    "VOICE"

                                                accent:
                                                    "#00CFFF"

                                                onTriggered: {

                                                    jarvisBridge
                                                    .listenMicrophone()
                                                }
                                            }


                                            ActionButton {
                                                Layout.preferredWidth:
                                                    88

                                                Layout.fillHeight:
                                                    true

                                                label:
                                                    "ABORT"

                                                accent:
                                                    "#FF4D6D"

                                                onTriggered: {

                                                    jarvisBridge
                                                    .stopResponse()
                                                }
                                            }


                                            ActionButton {
                                                Layout.preferredWidth:
                                                    88

                                                Layout.fillHeight:
                                                    true

                                                label:
                                                    "SEND"

                                                accent:
                                                    window.jarvisColor

                                                onTriggered: {

                                                    window.sendCurrentCommand()
                                                }
                                            }
                                        }
                                    }
                                }
                            }


                            // =====================================
                            // PAGE 1 - VOICE
                            // =====================================

                            Item {

                                RowLayout {
                                    anchors.fill:
                                        parent

                                    spacing:
                                        18


                                    Item {
                                        Layout.fillWidth:
                                            true

                                        Layout.fillHeight:
                                            true


                                        JarvisCore {
                                            anchors.centerIn:
                                                parent

                                            width:
                                                Math.min(
                                                    parent.width
                                                    * 0.78,

                                                    parent.height
                                                    * 0.78
                                                )

                                            height:
                                                width

                                            state:
                                                window.jarvisState

                                            accentColor:
                                                window.jarvisColor

                                            audioLevel:
                                                window.visualAudioLevel
                                        }
                                    }


                                    Rectangle {
                                        width:
                                            1

                                        Layout.fillHeight:
                                            true

                                        color:
                                            "#163542"
                                    }


                                    ColumnLayout {
                                        Layout.preferredWidth:
                                            340

                                        Layout.fillHeight:
                                            true

                                        spacing:
                                            12


                                        Text {
                                            text:
                                                "VOICE MATRIX"

                                            color:
                                                "#416E83"

                                            font.pixelSize:
                                                8

                                            font.letterSpacing:
                                                3
                                        }


                                        VoiceWave {
                                            Layout.fillWidth:
                                                true

                                            Layout.preferredHeight:
                                                130

                                            state:
                                                window.jarvisState

                                            accentColor:
                                                window.jarvisColor

                                            audioLevel:
                                                window.visualAudioLevel
                                        }


                                        InfoCard {
                                            Layout.fillWidth:
                                                true

                                            title:
                                                "STATUS"

                                            value:
                                                window.jarvisState

                                            accent:
                                                window.jarvisColor
                                        }


                                        InfoCard {
                                            Layout.fillWidth:
                                                true

                                            title:
                                                "MIC INPUT"

                                            value:
                                                Math.round(
                                                    window.inputAudioLevel
                                                    * 100
                                                )
                                                + "%"

                                            accent:
                                                "#00CFFF"
                                        }


                                        InfoCard {
                                            Layout.fillWidth:
                                                true

                                            title:
                                                "VOICE OUTPUT"

                                            value:
                                                Math.round(
                                                    window.outputAudioLevel
                                                    * 100
                                                )
                                                + "%"

                                            accent:
                                                "#8B7CFF"
                                        }


                                        Item {
                                            Layout.fillHeight:
                                                true
                                        }


                                        ActionButton {
                                            Layout.fillWidth:
                                                true

                                            label:
                                                "START LISTENING"

                                            accent:
                                                window.jarvisColor

                                            onTriggered: {

                                                jarvisBridge
                                                .listenMicrophone()
                                            }
                                        }


                                        ActionButton {
                                            Layout.fillWidth:
                                                true

                                            label:
                                                "ABORT RESPONSE"

                                            accent:
                                                "#FF4D6D"

                                            onTriggered: {

                                                jarvisBridge
                                                .stopResponse()
                                            }
                                        }
                                    }
                                }
                            }


                            // =====================================
                            // PAGE 2 - MEMORY
                            // =====================================

                            Item {

                                ColumnLayout {
                                    anchors.fill:
                                        parent

                                    spacing:
                                        10


                                    RowLayout {
                                        Layout.fillWidth:
                                            true

                                        spacing:
                                            10


                                        MemoryStatCard {
                                            Layout.fillWidth:
                                                true

                                            title:
                                                "TOTAL MEMORIES"

                                            value:
                                                window.memoryTotal
                                                .toString()

                                            accent:
                                                "#00CFFF"
                                        }


                                        MemoryStatCard {
                                            Layout.fillWidth:
                                                true

                                            title:
                                                "SEMANTIC INDEX"

                                            value:
                                                window.semanticMemoryTotal
                                                .toString()

                                            accent:
                                                "#8B7CFF"
                                        }


                                        MemoryStatCard {
                                            Layout.fillWidth:
                                                true

                                            title:
                                                "MEMORY STATUS"

                                            value:
                                                window.memoryTotal
                                                > 0
                                                ? "ACTIVE"
                                                : "EMPTY"

                                            accent:
                                                window.memoryTotal
                                                > 0
                                                ? "#00E59B"
                                                : "#FFC857"
                                        }
                                    }


                                    Rectangle {
                                        Layout.fillWidth:
                                            true

                                        Layout.preferredHeight:
                                            48

                                        radius:
                                            6

                                        color:
                                            "#85061118"

                                        border.width:
                                            1

                                        border.color:
                                            window.memoryStatusSuccess
                                            ? "#235C4D"
                                            : "#6A2635"


                                        RowLayout {
                                            anchors.fill:
                                                parent

                                            anchors.leftMargin:
                                                12

                                            anchors.rightMargin:
                                                12

                                            spacing:
                                                8


                                            Text {
                                                text:
                                                    "●"

                                                color:
                                                    window.memoryStatusSuccess
                                                    ? "#00E59B"
                                                    : "#FF4D6D"

                                                font.pixelSize:
                                                    10
                                            }


                                            Text {
                                                Layout.fillWidth:
                                                    true

                                                text:
                                                    window.memoryStatusMessage

                                                color:
                                                    "#9AB7C4"

                                                elide:
                                                    Text.ElideRight

                                                font.pixelSize:
                                                    9
                                            }


                                            Text {
                                                text:
                                                    "REAL MEMORY SERVICE"

                                                color:
                                                    "#406B7D"

                                                font.pixelSize:
                                                    7

                                                font.letterSpacing:
                                                    2
                                            }
                                        }
                                    }


                                    RowLayout {
                                        Layout.fillWidth:
                                            true

                                        spacing:
                                            8


                                        ActionButton {
                                            Layout.preferredWidth:
                                                130

                                            label:
                                                "REFRESH"

                                            accent:
                                                "#00CFFF"

                                            onTriggered: {

                                                jarvisBridge
                                                .loadMemory()
                                            }
                                        }


                                        ActionButton {
                                            Layout.preferredWidth:
                                                170

                                            label:
                                                "REBUILD INDEX"

                                            accent:
                                                "#8B7CFF"

                                            onTriggered: {

                                                jarvisBridge
                                                .rebuildMemoryIndex()
                                            }
                                        }


                                        Item {
                                            Layout.fillWidth:
                                                true
                                        }


                                        ActionButton {
                                            Layout.preferredWidth:
                                                190

                                            label:
                                                window.clearMemoryArmed
                                                ? "CONFIRM CLEAR ALL"
                                                : "CLEAR ALL MEMORY"

                                            accent:
                                                window.clearMemoryArmed
                                                ? "#FF254F"
                                                : "#8B3346"


                                            onTriggered: {

                                                if (
                                                    !window.clearMemoryArmed
                                                ) {

                                                    window.clearMemoryArmed =
                                                        true

                                                    clearMemoryTimer.restart()

                                                    window.memoryStatusMessage =
                                                        "Premi di nuovo CLEAR ALL entro 5 secondi."

                                                    window.memoryStatusSuccess =
                                                        false

                                                    return
                                                }

                                                clearMemoryTimer.stop()

                                                window.clearMemoryArmed =
                                                    false

                                                jarvisBridge.clearMemory()
                                            }
                                        }
                                    }


                                    Rectangle {
                                        Layout.fillWidth:
                                            true

                                        Layout.fillHeight:
                                            true

                                        radius:
                                            7

                                        color:
                                            "#8A030B10"

                                        border.width:
                                            1

                                        border.color:
                                            "#1B4658"


                                        ListView {
                                            id: memoryListView

                                            anchors.fill:
                                                parent

                                            anchors.margins:
                                                8

                                            model:
                                                memoryModel

                                            clip:
                                                true

                                            spacing:
                                                8


                                            header:
                                                Rectangle {

                                                width:
                                                    memoryListView.width

                                                height:
                                                    38

                                                color:
                                                    "transparent"


                                                RowLayout {
                                                    anchors.fill:
                                                        parent

                                                    anchors.leftMargin:
                                                        10

                                                    anchors.rightMargin:
                                                        10


                                                    Text {
                                                        text:
                                                            "STORED MEMORY"

                                                        color:
                                                            "#4E7A8E"

                                                        font.pixelSize:
                                                            7

                                                        font.letterSpacing:
                                                            3
                                                    }


                                                    Item {
                                                        Layout.fillWidth:
                                                            true
                                                    }


                                                    Text {
                                                        text:
                                                            memoryModel.count
                                                            + " RECORDS"

                                                        color:
                                                            "#3F6C7E"

                                                        font.pixelSize:
                                                            7
                                                    }
                                                }
                                            }


                                            delegate:
                                                Rectangle {

                                                id: memoryCard

                                                required property int memoryId
                                                required property string memoryKey
                                                required property string memoryValue
                                                required property string memoryType
                                                required property int importance
                                                required property string createdAt
                                                required property string updatedAt

                                                width:
                                                    memoryListView.width

                                                height:
                                                    Math.max(
                                                        120,
                                                        memoryContent
                                                        .implicitHeight
                                                        + 28
                                                    )

                                                radius:
                                                    7

                                                color:
                                                    memoryMouse.containsMouse
                                                    ? "#B00B1B24"
                                                    : "#99061118"

                                                border.width:
                                                    1

                                                border.color:
                                                    window.memoryTypeColor(
                                                        memoryCard.memoryType
                                                    )


                                                RowLayout {
                                                    anchors.fill:
                                                        parent

                                                    anchors.margins:
                                                        14

                                                    spacing:
                                                        12


                                                    Rectangle {
                                                        Layout.preferredWidth:
                                                            8

                                                        Layout.fillHeight:
                                                            true

                                                        radius:
                                                            4

                                                        color:
                                                            window.memoryTypeColor(
                                                                memoryCard.memoryType
                                                            )
                                                    }


                                                    ColumnLayout {
                                                        id: memoryContent

                                                        Layout.fillWidth:
                                                            true

                                                        spacing:
                                                            6


                                                        RowLayout {
                                                            Layout.fillWidth:
                                                                true


                                                            Text {
                                                                text:
                                                                    memoryCard
                                                                    .memoryType
                                                                    .toUpperCase()

                                                                color:
                                                                    window
                                                                    .memoryTypeColor(
                                                                        memoryCard.memoryType
                                                                    )

                                                                font.pixelSize:
                                                                    7

                                                                font.letterSpacing:
                                                                    1
                                                            }


                                                            Text {
                                                                text:
                                                                    "ID // "
                                                                    + (
                                                                        memoryCard.memoryId
                                                                        >= 0
                                                                        ? memoryCard.memoryId
                                                                        : "--"
                                                                    )

                                                                color:
                                                                    "#476A79"

                                                                font.pixelSize:
                                                                    7
                                                            }


                                                            Item {
                                                                Layout.fillWidth:
                                                                    true
                                                            }


                                                            Text {
                                                                text:
                                                                    "IMPORTANCE // "
                                                                    + memoryCard.importance
                                                                    + "/10"

                                                                color:
                                                                    memoryCard.importance
                                                                    >= 8
                                                                    ? "#FFC857"
                                                                    : "#658695"

                                                                font.pixelSize:
                                                                    7
                                                            }
                                                        }


                                                        Text {
                                                            Layout.fillWidth:
                                                                true

                                                            text:
                                                                memoryCard.memoryKey

                                                            color:
                                                                "#E3F5FC"

                                                            wrapMode:
                                                                Text.Wrap

                                                            font.pixelSize:
                                                                12

                                                            font.weight:
                                                                Font.DemiBold
                                                        }


                                                        Text {
                                                            Layout.fillWidth:
                                                                true

                                                            text:
                                                                memoryCard.memoryValue

                                                            color:
                                                                "#8FB0BD"

                                                            wrapMode:
                                                                Text.Wrap

                                                            font.pixelSize:
                                                                10

                                                            lineHeight:
                                                                1.25
                                                        }


                                                        RowLayout {
                                                            Layout.fillWidth:
                                                                true


                                                            Text {
                                                                text:
                                                                    "CREATED // "
                                                                    + memoryCard.createdAt

                                                                color:
                                                                    "#466B7B"

                                                                font.pixelSize:
                                                                    7
                                                            }


                                                            Text {
                                                                visible:
                                                                    memoryCard.updatedAt
                                                                    !== "--"

                                                                text:
                                                                    "UPDATED // "
                                                                    + memoryCard.updatedAt

                                                                color:
                                                                    "#466B7B"

                                                                font.pixelSize:
                                                                    7
                                                            }


                                                            Item {
                                                                Layout.fillWidth:
                                                                    true
                                                            }
                                                        }
                                                    }


                                                    ActionButton {
                                                        Layout.preferredWidth:
                                                            80

                                                        label:
                                                            "DELETE"

                                                        accent:
                                                            "#FF4D6D"

                                                        onTriggered: {

                                                            if (
                                                                memoryCard.memoryId
                                                                >= 0
                                                            ) {

                                                                jarvisBridge
                                                                .deleteMemory(
                                                                    memoryCard.memoryId
                                                                )
                                                            }
                                                        }
                                                    }
                                                }


                                                MouseArea {
                                                    id: memoryMouse

                                                    anchors.fill:
                                                        parent

                                                    acceptedButtons:
                                                        Qt.NoButton

                                                    hoverEnabled:
                                                        true
                                                }
                                            }


                                            Text {
                                                anchors.centerIn:
                                                    parent

                                                visible:
                                                    memoryModel.count
                                                    === 0

                                                text:
                                                    "NO MEMORIES STORED\n\nJ.A.R.V.I.S. will learn from future conversations."

                                                horizontalAlignment:
                                                    Text.AlignHCenter

                                                color:
                                                    "#476B7B"

                                                font.pixelSize:
                                                    11

                                                lineHeight:
                                                    1.4
                                            }
                                        }
                                    }
                                }
                            }


                            // =====================================
                            // PAGE 3 - PROJECTS
                            // =====================================

                            Item {

                                ColumnLayout {
                                    anchors.fill:
                                        parent

                                    spacing:
                                        12


                                    SectionHero {
                                        Layout.fillWidth:
                                            true

                                        title:
                                            "PROJECT COMMAND CENTER"

                                        description:
                                            "Accesso rapido agli strumenti principali del progetto J.A.R.V.I.S."
                                    }


                                    GridLayout {
                                        Layout.fillWidth:
                                            true

                                        Layout.fillHeight:
                                            true

                                        columns:
                                            2

                                        columnSpacing:
                                            12

                                        rowSpacing:
                                            12


                                        ActionCard {
                                            Layout.fillWidth:
                                                true

                                            Layout.fillHeight:
                                                true

                                            title:
                                                "J.A.R.V.I.S. DEVELOPMENT"

                                            subtitle:
                                                "Visual Studio Code"

                                            command:
                                                "apri visual studio code"

                                            accent:
                                                "#00CFFF"
                                        }


                                        ActionCard {
                                            Layout.fillWidth:
                                                true

                                            Layout.fillHeight:
                                                true

                                            title:
                                                "AI WORKSPACE"

                                            subtitle:
                                                "Microsoft Edge"

                                            command:
                                                "apri edge"

                                            accent:
                                                "#8B7CFF"
                                        }


                                        ActionCard {
                                            Layout.fillWidth:
                                                true

                                            Layout.fillHeight:
                                                true

                                            title:
                                                "MUSIC"

                                            subtitle:
                                                "Spotify"

                                            command:
                                                "apri spotify"

                                            accent:
                                                "#00E59B"
                                        }


                                        ActionCard {
                                            Layout.fillWidth:
                                                true

                                            Layout.fillHeight:
                                                true

                                            title:
                                                "WORK ROUTINE"

                                            subtitle:
                                                "Modalità lavoro"

                                            command:
                                                "modalità lavoro"

                                            accent:
                                                "#FFC857"
                                        }
                                    }
                                }
                            }


                            // =====================================
                            // PAGE 4 - TOOLS
                            // =====================================

                            Item {

                                ColumnLayout {
                                    anchors.fill:
                                        parent

                                    spacing:
                                        12


                                    SectionHero {
                                        Layout.fillWidth:
                                            true

                                        title:
                                            "DIRECT TOOLS"

                                        description:
                                            "Comandi diretti inviati alla stessa pipeline utilizzata dalla voce."
                                    }


                                    GridLayout {
                                        Layout.fillWidth:
                                            true

                                        Layout.fillHeight:
                                            true

                                        columns:
                                            3

                                        columnSpacing:
                                            12

                                        rowSpacing:
                                            12


                                        ActionCard {
                                            Layout.fillWidth:
                                                true

                                            Layout.fillHeight:
                                                true

                                            title:
                                                "SPOTIFY"

                                            subtitle:
                                                "Apri applicazione"

                                            command:
                                                "apri spotify"

                                            accent:
                                                "#00E59B"
                                        }


                                        ActionCard {
                                            Layout.fillWidth:
                                                true

                                            Layout.fillHeight:
                                                true

                                            title:
                                                "VS CODE"

                                            subtitle:
                                                "Apri editor"

                                            command:
                                                "apri visual studio code"

                                            accent:
                                                "#00CFFF"
                                        }


                                        ActionCard {
                                            Layout.fillWidth:
                                                true

                                            Layout.fillHeight:
                                                true

                                            title:
                                                "EDGE"

                                            subtitle:
                                                "Apri browser"

                                            command:
                                                "apri edge"

                                            accent:
                                                "#4FA7FF"
                                        }


                                        ActionCard {
                                            Layout.fillWidth:
                                                true

                                            Layout.fillHeight:
                                                true

                                            title:
                                                "OUTLOOK"

                                            subtitle:
                                                "Apri posta"

                                            command:
                                                "apri outlook"

                                            accent:
                                                "#5E84FF"
                                        }


                                        ActionCard {
                                            Layout.fillWidth:
                                                true

                                            Layout.fillHeight:
                                                true

                                            title:
                                                "WORD"

                                            subtitle:
                                                "Apri Word"

                                            command:
                                                "apri word"

                                            accent:
                                                "#2E78FF"
                                        }


                                        ActionCard {
                                            Layout.fillWidth:
                                                true

                                            Layout.fillHeight:
                                                true

                                            title:
                                                "EXCEL"

                                            subtitle:
                                                "Apri Excel"

                                            command:
                                                "apri excel"

                                            accent:
                                                "#19C37D"
                                        }
                                    }
                                }
                            }


                            // =====================================
                            // PAGE 5 - SYSTEM
                            // =====================================

                            Item {

                                RowLayout {
                                    anchors.fill:
                                        parent

                                    spacing:
                                        12


                                    ColumnLayout {
                                        Layout.fillWidth:
                                            true

                                        Layout.fillHeight:
                                            true

                                        spacing:
                                            10


                                        GraphCard {
                                            Layout.fillWidth:
                                                true

                                            Layout.fillHeight:
                                                true

                                            title:
                                                "CPU // PROCESSOR"

                                            value:
                                                window.cpuUsage
                                                .toFixed(0)
                                                + "%"

                                            history:
                                                window.cpuHistory

                                            accentColor:
                                                "#00CFFF"
                                        }


                                        GraphCard {
                                            Layout.fillWidth:
                                                true

                                            Layout.fillHeight:
                                                true

                                            title:
                                                "RAM // MEMORY"

                                            value:
                                                window.ramUsage
                                                .toFixed(0)
                                                + "%"

                                            history:
                                                window.ramHistory

                                            accentColor:
                                                "#8B7CFF"
                                        }


                                        GraphCard {
                                            Layout.fillWidth:
                                                true

                                            Layout.fillHeight:
                                                true

                                            title:
                                                "GPU // NVIDIA"

                                            value:
                                                window.gpuUsage
                                                .toFixed(0)
                                                + "%"

                                            history:
                                                window.gpuHistory

                                            accentColor:
                                                "#00E59B"
                                        }
                                    }


                                    ColumnLayout {
                                        Layout.preferredWidth:
                                            350

                                        Layout.fillHeight:
                                            true

                                        spacing:
                                            10


                                        TelemetryCard {
                                            Layout.fillWidth:
                                                true

                                            code:
                                                "DSK-01"

                                            title:
                                                "STORAGE"

                                            value:
                                                window.diskUsage
                                                .toFixed(0)
                                                + "%"

                                            description:
                                                "System drive"

                                            level:
                                                window.diskUsage
                                                / 100

                                            accentColor:
                                                "#00E59B"
                                        }


                                        TelemetryCard {
                                            Layout.fillWidth:
                                                true

                                            code:
                                                "NET-02"

                                            title:
                                                "NETWORK"

                                            value:
                                                window.networkSpeed
                                                .toFixed(2)
                                                + " Mb/s"

                                            description:
                                                "Current traffic"

                                            level:
                                                Math.min(
                                                    window.networkSpeed
                                                    / 100,
                                                    1
                                                )

                                            accentColor:
                                                "#FFC857"
                                        }


                                        TelemetryCard {
                                            Layout.fillWidth:
                                                true

                                            code:
                                                "AUD-03"

                                            title:
                                                "AUDIO MATRIX"

                                            value:
                                                Math.round(
                                                    window.visualAudioLevel
                                                    * 100
                                                )
                                                + "%"

                                            description:
                                                "Live audio interface"

                                            level:
                                                window.visualAudioLevel

                                            accentColor:
                                                window.jarvisColor
                                        }


                                        InfoCard {
                                            Layout.fillWidth:
                                                true

                                            Layout.fillHeight:
                                                true

                                            title:
                                                "SYSTEM HEALTH"

                                            value:
                                                Math.round(
                                                    window.performance
                                                )
                                                + "%"

                                            accent:
                                                window.performance
                                                > 60
                                                ? "#00E59B"
                                                : "#FFC857"

                                            detail:
                                                "UPTIME // "
                                                + window.uptime
                                        }
                                    }
                                }
                            }


                            // =====================================
                            // PAGE 6 - AUTOMATION
                            // =====================================

                            Item {

                                ColumnLayout {
                                    anchors.fill:
                                        parent

                                    spacing:
                                        12


                                    SectionHero {
                                        Layout.fillWidth:
                                            true

                                        title:
                                            "AUTOMATION CONTROL"

                                        description:
                                            "Routine e comandi di sistema eseguiti direttamente da J.A.R.V.I.S."
                                    }


                                    GridLayout {
                                        Layout.fillWidth:
                                            true

                                        Layout.fillHeight:
                                            true

                                        columns:
                                            2

                                        columnSpacing:
                                            12

                                        rowSpacing:
                                            12


                                        ActionCard {
                                            Layout.fillWidth:
                                                true

                                            Layout.fillHeight:
                                                true

                                            title:
                                                "MODALITÀ LAVORO"

                                            subtitle:
                                                "Spotify + playlist + VS Code + Edge"

                                            command:
                                                "modalità lavoro"

                                            accent:
                                                "#00CFFF"
                                        }


                                        ActionCard {
                                            Layout.fillWidth:
                                                true

                                            Layout.fillHeight:
                                                true

                                            title:
                                                "SCREENSHOT"

                                            subtitle:
                                                "Cattura lo schermo"

                                            command:
                                                "fai uno screenshot"

                                            accent:
                                                "#8B7CFF"
                                        }


                                        ActionCard {
                                            Layout.fillWidth:
                                                true

                                            Layout.fillHeight:
                                                true

                                            title:
                                                "RESTART PC"

                                            subtitle:
                                                "Riavvia Windows"

                                            command:
                                                "riavvia il computer"

                                            accent:
                                                "#FFC857"
                                        }


                                        ActionCard {
                                            Layout.fillWidth:
                                                true

                                            Layout.fillHeight:
                                                true

                                            title:
                                                "SHUTDOWN PC"

                                            subtitle:
                                                "Spegni Windows"

                                            command:
                                                "spegni il computer"

                                            accent:
                                                "#FF4D6D"
                                        }
                                    }
                                }
                            }


                            // =====================================
                            // PAGE 7 - VISION
                            // =====================================

                            VisionPage {
                                frameSource:
                                    window.visionFrame

                                cameraOnline:
                                    window.visionCameraOnline

                                handsCount:
                                    window.visionHandsCount

                                gestureState:
                                    window.visionGesture

                                lastCommand:
                                    window.visionCommand

                                errorMessage:
                                    window.visionError

                                accentColor:
                                    window.jarvisColor
                            }
                        }
                    }
                }
            }
        }


        // ========================================================
        // BOOT SCREEN
        // ========================================================

        Rectangle {
            id: bootOverlay

            anchors.fill:
                parent

            visible:
                !window.bootFinished

            color:
                "#FC010306"


            Column {
                anchors.centerIn:
                    parent

                spacing:
                    18


                Text {
                    anchors.horizontalCenter:
                        parent.horizontalCenter

                    text:
                        "J . A . R . V . I . S ."

                    color:
                        "#F0FBFF"

                    font.pixelSize:
                        31

                    font.weight:
                        Font.DemiBold

                    font.letterSpacing:
                        7
                }


                Text {
                    anchors.horizontalCenter:
                        parent.horizontalCenter

                    text:
                        "ADVANCED PERSONAL INTELLIGENCE SYSTEM"

                    color:
                        "#4C839E"

                    font.pixelSize:
                        8

                    font.letterSpacing:
                        4
                }


                Item {
                    width:
                        280

                    height:
                        70


                    JarvisCore {
                        anchors.centerIn:
                            parent

                        width:
                            155

                        height:
                            155

                        state:
                            window.jarvisState

                        accentColor:
                            window.jarvisColor

                        audioLevel:
                            window.visualAudioLevel
                    }
                }


                Column {
                    anchors.horizontalCenter:
                        parent.horizontalCenter

                    spacing:
                        8


                    Text {
                        text:
                            "CORE MATRIX ........................ "
                            + (
                                window.bootPhaseTwo
                                ? "ONLINE"
                                : "INITIALIZING"
                            )

                        color:
                            window.bootPhaseTwo
                            ? "#00E59B"
                            : "#5A879B"

                        font.pixelSize:
                            8
                    }


                    Text {
                        text:
                            "VOICE LINK ......................... "
                            + (
                                window.bootPhaseTwo
                                ? "ONLINE"
                                : "STANDBY"
                            )

                        color:
                            window.bootPhaseTwo
                            ? "#00E59B"
                            : "#5A879B"

                        font.pixelSize:
                            8
                    }


                    Text {
                        text:
                            "MEMORY MATRIX ...................... "
                            + (
                                window.bootPhaseThree
                                ? "ONLINE"
                                : "WAIT"
                            )

                        color:
                            window.bootPhaseThree
                            ? "#00E59B"
                            : "#5A879B"

                        font.pixelSize:
                            8
                    }


                    Text {
                        text:
                            "VISION ENGINE ...................... "
                            + (
                                window.visionCameraOnline
                                ? "ONLINE"
                                : (
                                    window.bootPhaseThree
                                    ? "STARTING"
                                    : "WAIT"
                                )
                            )

                        color:
                            window.visionCameraOnline
                            ? "#00E59B"
                            : "#5A879B"

                        font.pixelSize:
                            8
                    }


                    Text {
                        text:
                            "AI ENGINE .......................... "
                            + (
                                window.bootPhaseThree
                                ? "READY"
                                : "WAIT"
                            )

                        color:
                            window.bootPhaseThree
                            ? "#00E59B"
                            : "#5A879B"

                        font.pixelSize:
                            8
                    }
                }


                Rectangle {
                    anchors.horizontalCenter:
                        parent.horizontalCenter

                    width:
                        290

                    height:
                        2

                    color:
                        "#173746"


                    Rectangle {
                        height:
                            parent.height

                        width:
                            window.bootPhaseThree
                            ? parent.width
                            : window.bootPhaseTwo
                              ? parent.width * 0.66
                              : parent.width * 0.30

                        color:
                            "#00CFFF"


                        Behavior on width {

                            NumberAnimation {
                                duration:
                                    600

                                easing.type:
                                    Easing.OutCubic
                            }
                        }
                    }
                }


                Text {
                    anchors.horizontalCenter:
                        parent.horizontalCenter

                    text:
                        window.bootPhaseThree
                        ? "SYSTEM READY"
                        : "INITIALIZING..."

                    color:
                        window.bootPhaseThree
                        ? "#00E59B"
                        : "#50859C"

                    font.pixelSize:
                        9

                    font.letterSpacing:
                        3
                }
            }
        }
    }


    // ============================================================
    // INLINE COMPONENT - ACTION BUTTON
    // ============================================================

    component ActionButton:
        Rectangle {

        id: actionButton

        property string label:
            ""

        property color accent:
            "#00D9FF"

        signal triggered()

        implicitHeight:
            46

        radius:
            6

        color:
            actionMouse.containsMouse
            ? Qt.rgba(
                accent.r,
                accent.g,
                accent.b,
                0.18
            )
            : "#09151C"

        border.width:
            1

        border.color:
            accent


        Text {
            anchors.centerIn:
                parent

            text:
                actionButton.label

            color:
                "#E7F8FF"

            font.pixelSize:
                8

            font.letterSpacing:
                1
        }


        MouseArea {
            id: actionMouse

            anchors.fill:
                parent

            hoverEnabled:
                true

            onClicked: {

                actionButton.triggered()
            }
        }
    }


    // ============================================================
    // INLINE COMPONENT - HERO
    // ============================================================

    component SectionHero:
        Rectangle {

        id: sectionHero

        property string title:
            ""

        property string description:
            ""

        implicitHeight:
            96

        radius:
            8

        color:
            "#AA06131B"

        border.width:
            1

        border.color:
            "#1C4D62"


        Column {
            anchors.fill:
                parent

            anchors.margins:
                16

            spacing:
                7


            Text {
                text:
                    sectionHero.title

                color:
                    "#E8F8FF"

                font.pixelSize:
                    16

                font.weight:
                    Font.DemiBold
            }


            Text {
                width:
                    parent.width

                text:
                    sectionHero.description

                color:
                    "#62899A"

                wrapMode:
                    Text.Wrap

                font.pixelSize:
                    10
            }
        }
    }


    // ============================================================
    // INLINE COMPONENT - INFO CARD
    // ============================================================

    component InfoCard:
        Rectangle {

        id: infoCard

        property string title:
            ""

        property string value:
            ""

        property string detail:
            ""

        property color accent:
            "#00D9FF"

        implicitHeight:
            110

        radius:
            7

        color:
            "#AA061019"

        border.width:
            1

        border.color:
            Qt.rgba(
                accent.r,
                accent.g,
                accent.b,
                0.35
            )


        Column {
            anchors.fill:
                parent

            anchors.margins:
                14

            spacing:
                7


            Text {
                text:
                    infoCard.title

                color:
                    "#52798B"

                font.pixelSize:
                    7

                font.letterSpacing:
                    2
            }


            Text {
                width:
                    parent.width

                text:
                    infoCard.value

                color:
                    infoCard.accent

                font.pixelSize:
                    24

                font.weight:
                    Font.Light

                elide:
                    Text.ElideRight
            }


            Text {
                width:
                    parent.width

                text:
                    infoCard.detail

                visible:
                    infoCard.detail.length
                    > 0

                color:
                    "#527080"

                wrapMode:
                    Text.Wrap

                font.pixelSize:
                    9
            }
        }
    }


    // ============================================================
    // INLINE COMPONENT - MEMORY STAT CARD
    // ============================================================

    component MemoryStatCard:
        Rectangle {

        id: memoryStat

        property string title:
            ""

        property string value:
            ""

        property color accent:
            "#00D9FF"

        implicitHeight:
            90

        radius:
            7

        color:
            "#AA061019"

        border.width:
            1

        border.color:
            Qt.rgba(
                accent.r,
                accent.g,
                accent.b,
                0.45
            )


        Column {
            anchors.fill:
                parent

            anchors.margins:
                13

            spacing:
                6


            Text {
                text:
                    memoryStat.title

                color:
                    "#50798B"

                font.pixelSize:
                    7

                font.letterSpacing:
                    2
            }


            Text {
                text:
                    memoryStat.value

                color:
                    memoryStat.accent

                font.pixelSize:
                    24

                font.weight:
                    Font.Light
            }
        }
    }


    // ============================================================
    // INLINE COMPONENT - ACTION CARD
    // ============================================================

    component ActionCard:
        Rectangle {

        id: actionCard

        property string title:
            ""

        property string subtitle:
            ""

        property string command:
            ""

        property color accent:
            "#00D9FF"

        radius:
            8

        color:
            cardMouse.containsMouse
            ? Qt.rgba(
                accent.r,
                accent.g,
                accent.b,
                0.14
            )
            : "#AA061019"

        border.width:
            1

        border.color:
            cardMouse.containsMouse
            ? accent
            : Qt.rgba(
                accent.r,
                accent.g,
                accent.b,
                0.35
            )


        Column {
            anchors.left:
                parent.left

            anchors.right:
                parent.right

            anchors.verticalCenter:
                parent.verticalCenter

            anchors.leftMargin:
                18

            anchors.rightMargin:
                18

            spacing:
                9


            Rectangle {
                width:
                    34

                height:
                    3

                radius:
                    2

                color:
                    actionCard.accent
            }


            Text {
                text:
                    actionCard.title

                color:
                    "#E9F8FF"

                font.pixelSize:
                    14

                font.weight:
                    Font.DemiBold
            }


            Text {
                width:
                    parent.width

                text:
                    actionCard.subtitle

                color:
                    "#5E8292"

                wrapMode:
                    Text.Wrap

                font.pixelSize:
                    9
            }


            Text {
                text:
                    "EXECUTE"

                color:
                    actionCard.accent

                font.pixelSize:
                    8

                font.letterSpacing:
                    2
            }
        }


        MouseArea {
            id: cardMouse

            anchors.fill:
                parent

            hoverEnabled:
                true


            onClicked: {

                if (
                    actionCard.command.length
                    > 0
                ) {

                    window.activePage =
                        0

                    window.sendCommandText(
                        actionCard.command
                    )
                }
            }
        }
    }


    // ============================================================
    // FUNCTIONS
    // ============================================================

    function sendCurrentCommand() {

        var command =
            commandField.text.trim()

        if (
            command.length
            === 0
        ) {

            return
        }

        commandField.text =
            ""

        sendCommandText(
            command
        )
    }


    function sendCommandText(
        command
    ) {

        var cleanCommand =
            command.trim()

        if (
            cleanCommand.length
            === 0
        ) {

            return
        }

        chatModel.append({
            "role":
                "RICCARDO // INPUT",

            "text":
                cleanCommand,

            "accent":
                "#79AABD"
        })


        if (
            chatView.count
            > 0
        ) {

            chatView.positionViewAtEnd()
        }


        jarvisBridge.sendCommand(
            cleanCommand
        )
    }


    function memoryTypeColor(
        memoryType
    ) {

        var type =
            memoryType.toLowerCase()


        if (
            type
            === "profile"
        ) {

            return "#00CFFF"
        }


        if (
            type
            === "preference"
        ) {

            return "#8B7CFF"
        }


        if (
            type
            === "project"
        ) {

            return "#00E59B"
        }


        if (
            type
            === "experience"
        ) {

            return "#FFC857"
        }


        return "#79AABD"
    }
}