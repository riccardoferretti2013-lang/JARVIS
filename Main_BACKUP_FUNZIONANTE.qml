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
    // STATE
    // ============================================================

    property string jarvisState: "STARTING"
    property color jarvisColor: "#00D9FF"

    property int activePage: 0
    property int currentStreamIndex: -1

    property point dragStart: Qt.point(0, 0)


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
    property bool visionCameraOnline: false
    property int visionHandsCount: 0
    property string visionGesture: "STARTING"
    property string visionCommand: "NONE"
    property string visionError: ""


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
        },
        {
            "label": "09   COMPANY",
            "title": "AI COMPANY",
            "subtitle": "VIRTUAL HEADQUARTERS"
        }
    ]


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
    // STARTUP
    // ============================================================

    Component.onCompleted: {
        jarvisBridge.start()
        visionBridge.start()
    }


    onClosing:
        function(close) {
            close.accepted = false
            window.hide()
        }


    // ============================================================
    // JARVIS BRIDGE
    // ============================================================

    Connections {
        target: jarvisBridge


        function onStateChanged(state, color) {
            window.jarvisState = state
            window.jarvisColor = color
        }


        function onAudioLevelChanged(source, level) {

            var safeLevel =
                Math.max(
                    0,
                    Math.min(1, level)
                )

            if (source === "input") {
                window.inputAudioLevel = safeLevel
            }

            if (source === "output") {
                window.outputAudioLevel = safeLevel
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

            window.cpuUsage = cpu
            window.ramUsage = memory
            window.diskUsage = disk
            window.networkSpeed = network
            window.gpuUsage = gpu
            window.performance = score
            window.uptime = uptimeText

            var cpuArray =
                window.cpuHistory.slice()

            cpuArray.push(cpu)

            if (cpuArray.length > 45) {
                cpuArray.shift()
            }

            window.cpuHistory =
                cpuArray


            var ramArray =
                window.ramHistory.slice()

            ramArray.push(memory)

            if (ramArray.length > 45) {
                ramArray.shift()
            }

            window.ramHistory =
                ramArray


            var gpuArray =
                window.gpuHistory.slice()

            gpuArray.push(gpu)

            if (gpuArray.length > 45) {
                gpuArray.shift()
            }

            window.gpuHistory =
                gpuArray
        }


        function onAssistantMessage(message) {

            chatModel.append({
                "role": "J.A.R.V.I.S.",
                "text": message,
                "accent": "#00D9FF"
            })

            chatView.positionViewAtEnd()
        }


        function onStreamStarted() {

            chatModel.append({
                "role": "J.A.R.V.I.S.",
                "text": "",
                "accent": "#00D9FF"
            })

            window.currentStreamIndex =
                chatModel.count - 1

            chatView.positionViewAtEnd()
        }


        function onStreamChunk(chunk) {

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

            chatView.positionViewAtEnd()
        }


        function onStreamFinished() {
            window.currentStreamIndex = -1
        }


        function onVoiceCommandDetected(command) {

            chatModel.append({
                "role": "RICCARDO // VOICE",
                "text": command,
                "accent": "#74A7BD"
            })

            chatView.positionViewAtEnd()
        }


        function onErrorOccurred(message) {

            chatModel.append({
                "role": "SYSTEM ERROR",
                "text": message,
                "accent": "#FF4D6D"
            })

            chatView.positionViewAtEnd()
        }


        // ========================================================
        // PAGE REQUEST
        // ========================================================

        function onPageRequested(pageName) {

            if (
                pageName === "company"
            ) {

                window.activePage = 8

                window.show()
                window.raise()
                window.requestActivate()
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

            if (
                operation === "clear"
                && success
            ) {

                window.clearMemoryArmed =
                    false
            }
        }
    }


    // ============================================================
    // VISION BRIDGE
    // ============================================================

    Connections {
        target: visionBridge


        function onFrameChanged(frameSource) {
            window.visionFrame = frameSource
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

            if (cameraOnline) {
                window.visionError = ""
            }
        }


        function onErrorOccurred(message) {
            window.visionCameraOnline = false
            window.visionError = message
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

                ctx.lineWidth = 1

                var spacing = 46


                for (
                    var x = 0;
                    x < width;
                    x += spacing
                ) {

                    ctx.beginPath()
                    ctx.moveTo(x, 0)
                    ctx.lineTo(x, height)
                    ctx.stroke()
                }


                for (
                    var y = 0;
                    y < height;
                    y += spacing
                ) {

                    ctx.beginPath()
                    ctx.moveTo(0, y)
                    ctx.lineTo(width, y)
                    ctx.stroke()
                }
            }
        }


        // ========================================================
        // MAIN LAYOUT
        // ========================================================

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 12

            spacing: 10


            // ====================================================
            // TITLE BAR
            // ====================================================

            GlassPanel {
                id: titleBar

                Layout.fillWidth: true
                Layout.preferredHeight: 68

                highlighted: true
                accentColor: window.jarvisColor


                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 18
                    anchors.rightMargin: 10

                    spacing: 12


                    ColumnLayout {
                        spacing: 1


                        Text {
                            text: "J . A . R . V . I . S ."

                            color: "#EAFBFF"

                            font.pixelSize: 17
                            font.weight: Font.DemiBold
                            font.letterSpacing: 4
                        }


                        Text {
                            text:
                                "JUST A RATHER VERY INTELLIGENT SYSTEM"

                            color: "#4F8299"

                            font.pixelSize: 7
                            font.letterSpacing: 2
                        }
                    }


                    Item {
                        Layout.fillWidth: true
                    }


                    Rectangle {
                        width: 10
                        height: 10
                        radius: 5

                        color: window.jarvisColor
                    }


                    Text {
                        text: window.jarvisState

                        color: window.jarvisColor

                        font.pixelSize: 9
                        font.letterSpacing: 2
                    }


                    Rectangle {
                        width: 1
                        height: 30

                        color: "#214150"
                    }


                    Button {
                        text: "—"

                        flat: true

                        onClicked: {
                            window.showMinimized()
                        }
                    }


                    Button {
                        text: "□"

                        flat: true

                        onClicked: {

                            if (
                                window.visibility
                                === Window.Maximized
                            ) {

                                window.showNormal()
                            }

                            else {
                                window.showMaximized()
                            }
                        }
                    }


                    Button {
                        text: "×"

                        flat: true

                        onClicked: {
                            window.hide()
                        }
                    }
                }


                MouseArea {
                    anchors.fill: parent

                    acceptedButtons:
                        Qt.LeftButton

                    z: -1

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
                                mouse.buttons
                                & Qt.LeftButton
                            ) {

                                window.x +=
                                    mouse.x
                                    - window.dragStart.x

                                window.y +=
                                    mouse.y
                                    - window.dragStart.y
                            }
                        }
                }
            }


            // ====================================================
            // BODY
            // ====================================================

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true

                spacing: 10


                // =================================================
                // SIDEBAR
                // =================================================

                GlassPanel {
                    Layout.preferredWidth: 225
                    Layout.fillHeight: true

                    accentColor: window.jarvisColor


                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12

                        spacing: 8


                        Text {
                            text: "SYSTEM MODULES"

                            color: "#50798B"

                            font.pixelSize: 7
                            font.letterSpacing: 3
                        }


                        Repeater {
                            model: window.navigationItems


                            delegate:
                                Rectangle {

                                required property int index
                                required property var modelData

                                Layout.fillWidth: true
                                Layout.preferredHeight: 48

                                radius: 5

                                color:
                                    window.activePage === index
                                    ? "#142B35"
                                    : "transparent"

                                border.width:
                                    window.activePage === index
                                    ? 1
                                    : 0

                                border.color:
                                    window.jarvisColor


                                Text {
                                    anchors.verticalCenter:
                                        parent.verticalCenter

                                    anchors.left:
                                        parent.left

                                    anchors.leftMargin:
                                        12

                                    text:
                                        modelData.label

                                    color:
                                        window.activePage === index
                                        ? "#EAFBFF"
                                        : "#648797"

                                    font.pixelSize: 9
                                    font.letterSpacing: 1
                                }


                                MouseArea {
                                    anchors.fill: parent
                                    hoverEnabled: true

                                    onClicked: {

                                        window.activePage =
                                            index

                                        if (index === 2) {
                                            jarvisBridge.loadMemory()
                                        }
                                    }
                                }
                            }
                        }


                        Item {
                            Layout.fillHeight: true
                        }


                        Text {
                            text: "CORE // ONLINE"

                            color: "#00E59B"

                            font.pixelSize: 7
                            font.letterSpacing: 2
                        }


                        Text {
                            text:
                                "UPTIME // "
                                + window.uptime

                            color: "#466D7E"

                            font.pixelSize: 7
                        }
                    }
                }


                // =================================================
                // CONTENT
                // =================================================

                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    spacing: 10


                    GlassPanel {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 72

                        accentColor: window.jarvisColor


                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 18
                            anchors.rightMargin: 18


                            ColumnLayout {
                                spacing: 2


                                Text {
                                    text:
                                        window
                                        .navigationItems[
                                            window.activePage
                                        ]
                                        .title

                                    color: "#EAFBFF"

                                    font.pixelSize: 19
                                    font.weight: Font.DemiBold
                                }


                                Text {
                                    text:
                                        window
                                        .navigationItems[
                                            window.activePage
                                        ]
                                        .subtitle

                                    color: "#527B8E"

                                    font.pixelSize: 8
                                    font.letterSpacing: 2
                                }
                            }


                            Item {
                                Layout.fillWidth: true
                            }


                            Text {
                                text:
                                    "STATE // "
                                    + window.jarvisState

                                color:
                                    window.jarvisColor

                                font.pixelSize: 8
                                font.letterSpacing: 2
                            }
                        }
                    }


                    // =============================================
                    // PAGES
                    // =============================================

                    StackLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true

                        currentIndex:
                            window.activePage


                        // =========================================
                        // 0 - CHAT
                        // =========================================

                        Item {

                            ColumnLayout {
                                anchors.fill: parent

                                spacing: 10


                                GlassPanel {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    accentColor:
                                        window.jarvisColor


                                    ListView {
                                        id: chatView

                                        anchors.fill: parent
                                        anchors.margins: 12

                                        model: chatModel

                                        spacing: 8
                                        clip: true


                                        delegate:
                                            Rectangle {

                                            required property string role
                                            required property string text
                                            required property string accent

                                            width:
                                                chatView.width

                                            height:
                                                messageColumn
                                                .implicitHeight
                                                + 24

                                            radius: 6

                                            color:
                                                "#7A061119"

                                            border.width: 1

                                            border.color:
                                                Qt.rgba(
                                                    0,
                                                    0.85,
                                                    1,
                                                    0.18
                                                )


                                            Column {
                                                id: messageColumn

                                                anchors.left:
                                                    parent.left

                                                anchors.right:
                                                    parent.right

                                                anchors.top:
                                                    parent.top

                                                anchors.margins:
                                                    12

                                                spacing: 6


                                                Text {
                                                    text: role

                                                    color: accent

                                                    font.pixelSize: 7
                                                    font.letterSpacing: 2
                                                }


                                                Text {
                                                    width:
                                                        parent.width

                                                    text:
                                                        parent
                                                        .parent
                                                        .text

                                                    color: "#D6EAF2"

                                                    wrapMode:
                                                        Text.Wrap

                                                    font.pixelSize: 11
                                                }
                                            }
                                        }
                                    }
                                }


                                RowLayout {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 52

                                    spacing: 8


                                    TextField {
                                        id: commandInput

                                        Layout.fillWidth: true
                                        Layout.fillHeight: true

                                        placeholderText:
                                            "Scrivi un comando..."

                                        color: "#EAFBFF"

                                        background:
                                            Rectangle {

                                            radius: 6

                                            color: "#07131A"

                                            border.width: 1
                                            border.color: "#1B5269"
                                        }


                                        onAccepted: {
                                            window.sendTextCommand()
                                        }
                                    }


                                    ActionButton {
                                        Layout.preferredWidth: 110

                                        label: "SEND"
                                        accent: "#00CFFF"

                                        onTriggered: {
                                            window.sendTextCommand()
                                        }
                                    }


                                    ActionButton {
                                        Layout.preferredWidth: 110

                                        label: "VOICE"
                                        accent: "#8B7CFF"

                                        onTriggered: {
                                            jarvisBridge.listenMicrophone()
                                        }
                                    }
                                }
                            }
                        }


                        // =========================================
                        // 1 - VOICE
                        // =========================================

                        Item {

                            RowLayout {
                                anchors.fill: parent

                                spacing: 18


                                Item {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true


                                    JarvisCore {
                                        anchors.centerIn: parent

                                        width:
                                            Math.min(
                                                parent.width * 0.72,
                                                parent.height * 0.72
                                            )

                                        height: width

                                        state:
                                            window.jarvisState

                                        accentColor:
                                            window.jarvisColor

                                        audioLevel:
                                            window.visualAudioLevel
                                    }
                                }


                                GlassPanel {
                                    Layout.preferredWidth: 360
                                    Layout.fillHeight: true

                                    accentColor:
                                        window.jarvisColor


                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 16

                                        spacing: 12


                                        Text {
                                            text: "VOICE MATRIX"

                                            color: "#527B8E"

                                            font.pixelSize: 8
                                            font.letterSpacing: 3
                                        }


                                        VoiceWave {
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: 140

                                            state:
                                                window.jarvisState

                                            accentColor:
                                                window.jarvisColor

                                            audioLevel:
                                                window.visualAudioLevel
                                        }


                                        InfoCard {
                                            Layout.fillWidth: true

                                            title: "STATUS"

                                            value:
                                                window.jarvisState

                                            accent:
                                                window.jarvisColor
                                        }


                                        InfoCard {
                                            Layout.fillWidth: true

                                            title: "MIC INPUT"

                                            value:
                                                Math.round(
                                                    window.inputAudioLevel
                                                    * 100
                                                )
                                                + "%"

                                            accent: "#00CFFF"
                                        }


                                        Item {
                                            Layout.fillHeight: true
                                        }


                                        ActionButton {
                                            Layout.fillWidth: true

                                            label:
                                                "START LISTENING"

                                            accent:
                                                "#00CFFF"

                                            onTriggered: {
                                                jarvisBridge.listenMicrophone()
                                            }
                                        }


                                        ActionButton {
                                            Layout.fillWidth: true

                                            label:
                                                "ABORT RESPONSE"

                                            accent:
                                                "#FF4D6D"

                                            onTriggered: {
                                                jarvisBridge.stopResponse()
                                            }
                                        }
                                    }
                                }
                            }
                        }


                        // =========================================
                        // 2 - MEMORY
                        // =========================================

                        Item {

                            ColumnLayout {
                                anchors.fill: parent

                                spacing: 10


                                RowLayout {
                                    Layout.fillWidth: true

                                    spacing: 10


                                    InfoCard {
                                        Layout.fillWidth: true

                                        title:
                                            "TOTAL MEMORIES"

                                        value:
                                            window.memoryTotal
                                            .toString()

                                        accent:
                                            "#00CFFF"
                                    }


                                    InfoCard {
                                        Layout.fillWidth: true

                                        title:
                                            "SEMANTIC INDEX"

                                        value:
                                            window.semanticMemoryTotal
                                            .toString()

                                        accent:
                                            "#8B7CFF"
                                    }


                                    ActionButton {
                                        Layout.preferredWidth: 130

                                        label: "REFRESH"
                                        accent: "#00CFFF"

                                        onTriggered: {
                                            jarvisBridge.loadMemory()
                                        }
                                    }


                                    ActionButton {
                                        Layout.preferredWidth: 160

                                        label:
                                            "REBUILD INDEX"

                                        accent:
                                            "#8B7CFF"

                                        onTriggered: {
                                            jarvisBridge.rebuildMemoryIndex()
                                        }
                                    }
                                }


                                GlassPanel {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    accentColor: "#00CFFF"


                                    ListView {
                                        anchors.fill: parent
                                        anchors.margins: 10

                                        model: memoryModel

                                        clip: true
                                        spacing: 8


                                        delegate:
                                            Rectangle {

                                            required property int memoryId
                                            required property string memoryKey
                                            required property string memoryValue
                                            required property string memoryType
                                            required property int importance
                                            required property string createdAt
                                            required property string updatedAt

                                            width:
                                                ListView.view.width

                                            height:
                                                memoryText
                                                .implicitHeight
                                                + 38

                                            radius: 6

                                            color:
                                                "#85061118"

                                            border.width: 1

                                            border.color:
                                                window.memoryTypeColor(
                                                    memoryType
                                                )


                                            Column {
                                                id: memoryText

                                                anchors.left:
                                                    parent.left

                                                anchors.right:
                                                    parent.right

                                                anchors.top:
                                                    parent.top

                                                anchors.margins:
                                                    12

                                                spacing: 5


                                                Text {
                                                    text:
                                                        memoryType
                                                        .toUpperCase()
                                                        + " // "
                                                        + memoryKey

                                                    color:
                                                        window.memoryTypeColor(
                                                            memoryType
                                                        )

                                                    font.pixelSize: 8
                                                    font.letterSpacing: 1
                                                }


                                                Text {
                                                    width:
                                                        parent.width

                                                    text:
                                                        memoryValue

                                                    color:
                                                        "#C3DCE6"

                                                    wrapMode:
                                                        Text.Wrap

                                                    font.pixelSize: 10
                                                }


                                                Text {
                                                    text:
                                                        "IMPORTANCE // "
                                                        + importance
                                                        + "/10"

                                                    color:
                                                        "#52798B"

                                                    font.pixelSize: 7
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }


                        // =========================================
                        // 3 - PROJECTS
                        // =========================================

                        Item {

                            GridLayout {
                                anchors.fill: parent

                                columns: 2

                                columnSpacing: 12
                                rowSpacing: 12


                                ActionCard {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

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
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

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
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

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
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

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


                        // =========================================
                        // 4 - TOOLS
                        // =========================================

                        Item {

                            GridLayout {
                                anchors.fill: parent

                                columns: 3

                                columnSpacing: 12
                                rowSpacing: 12


                                ActionCard {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    title: "SPOTIFY"
                                    subtitle: "Apri applicazione"
                                    command: "apri spotify"
                                    accent: "#00E59B"
                                }


                                ActionCard {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    title: "VS CODE"
                                    subtitle: "Apri editor"
                                    command: "apri visual studio code"
                                    accent: "#00CFFF"
                                }


                                ActionCard {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    title: "EDGE"
                                    subtitle: "Apri browser"
                                    command: "apri edge"
                                    accent: "#4FA7FF"
                                }


                                ActionCard {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    title: "OUTLOOK"
                                    subtitle: "Apri posta"
                                    command: "apri outlook"
                                    accent: "#5E84FF"
                                }


                                ActionCard {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    title: "WORD"
                                    subtitle: "Apri Word"
                                    command: "apri word"
                                    accent: "#2E78FF"
                                }


                                ActionCard {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    title: "EXCEL"
                                    subtitle: "Apri Excel"
                                    command: "apri excel"
                                    accent: "#19C37D"
                                }
                            }
                        }


                        // =========================================
                        // 5 - SYSTEM
                        // =========================================

                        Item {

                            GridLayout {
                                anchors.fill: parent

                                columns: 2

                                columnSpacing: 12
                                rowSpacing: 12


                                InfoCard {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    title: "CPU // PROCESSOR"

                                    value:
                                        window.cpuUsage
                                        .toFixed(0)
                                        + "%"

                                    accent: "#00CFFF"
                                }


                                InfoCard {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    title: "RAM // MEMORY"

                                    value:
                                        window.ramUsage
                                        .toFixed(0)
                                        + "%"

                                    accent: "#8B7CFF"
                                }


                                InfoCard {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    title: "GPU // NVIDIA"

                                    value:
                                        window.gpuUsage
                                        .toFixed(0)
                                        + "%"

                                    accent: "#00E59B"
                                }


                                InfoCard {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    title: "STORAGE"

                                    value:
                                        window.diskUsage
                                        .toFixed(0)
                                        + "%"

                                    accent: "#FFC857"
                                }


                                InfoCard {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    title: "NETWORK"

                                    value:
                                        window.networkSpeed
                                        .toFixed(2)
                                        + " Mb/s"

                                    accent: "#4FA7FF"
                                }


                                InfoCard {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    title: "SYSTEM HEALTH"

                                    value:
                                        Math.round(
                                            window.performance
                                        )
                                        + "%"

                                    accent:
                                        window.performance > 60
                                        ? "#00E59B"
                                        : "#FFC857"
                                }
                            }
                        }


                        // =========================================
                        // 6 - AUTOMATION
                        // =========================================

                        Item {

                            GridLayout {
                                anchors.fill: parent

                                columns: 2

                                columnSpacing: 12
                                rowSpacing: 12


                                ActionCard {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

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
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

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
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

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
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

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


                        // =========================================
                        // 7 - VISION
                        // =========================================

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


                        // =========================================
                        // 8 - AI COMPANY
                        // =========================================

                        CompanyPage {
                            accentColor:
                                "#00D9FF"
                        }
                    }
                }
            }
        }
    }


    // ============================================================
    // ACTION BUTTON
    // ============================================================

    component ActionButton:
        Rectangle {

        id: actionButton

        property string label: ""
        property color accent: "#00D9FF"

        signal triggered()

        implicitHeight: 46

        radius: 6
        color: "#09151C"

        border.width: 1
        border.color: accent


        Text {
            anchors.centerIn: parent

            text:
                actionButton.label

            color: "#E7F8FF"

            font.pixelSize: 8
            font.letterSpacing: 1
        }


        MouseArea {
            anchors.fill: parent
            hoverEnabled: true

            onClicked: {
                actionButton.triggered()
            }
        }
    }


    // ============================================================
    // INFO CARD
    // ============================================================

    component InfoCard:
        Rectangle {

        id: infoCard

        property string title: ""
        property string value: ""
        property color accent: "#00D9FF"

        implicitHeight: 100

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

            spacing: 7


            Text {
                text:
                    infoCard.title

                color: "#52798B"

                font.pixelSize: 7
                font.letterSpacing: 2
            }


            Text {
                width: parent.width

                text:
                    infoCard.value

                color:
                    infoCard.accent

                font.pixelSize: 23
                font.weight: Font.Light

                elide: Text.ElideRight
            }
        }
    }


    // ============================================================
    // ACTION CARD
    // ============================================================

    component ActionCard:
        Rectangle {

        id: actionCard

        property string title: ""
        property string subtitle: ""
        property string command: ""
        property color accent: "#00D9FF"

        radius: 8

        color:
            actionMouse.containsMouse
            ? Qt.rgba(
                accent.r,
                accent.g,
                accent.b,
                0.14
            )
            : "#AA061019"

        border.width: 1

        border.color:
            actionMouse.containsMouse
            ? accent
            : Qt.rgba(
                accent.r,
                accent.g,
                accent.b,
                0.35
            )


        Column {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter

            anchors.leftMargin: 18
            anchors.rightMargin: 18

            spacing: 9


            Rectangle {
                width: 34
                height: 3
                radius: 2

                color:
                    actionCard.accent
            }


            Text {
                text:
                    actionCard.title

                color: "#E9F8FF"

                font.pixelSize: 14
                font.weight: Font.DemiBold
            }


            Text {
                width: parent.width

                text:
                    actionCard.subtitle

                color: "#5E8292"

                wrapMode: Text.Wrap

                font.pixelSize: 9
            }


            Text {
                text: "EXECUTE"

                color:
                    actionCard.accent

                font.pixelSize: 8
                font.letterSpacing: 2
            }
        }


        MouseArea {
            id: actionMouse

            anchors.fill: parent
            hoverEnabled: true


            onClicked: {

                if (
                    actionCard.command.length
                    > 0
                ) {

                    window.activePage = 0

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

    function sendTextCommand() {

        var command =
            commandInput.text.trim()

        if (
            command.length === 0
        ) {
            return
        }

        commandInput.text = ""

        sendCommandText(command)
    }


    function sendCommandText(command) {

        var cleanCommand =
            command.trim()

        if (
            cleanCommand.length === 0
        ) {
            return
        }

        chatModel.append({
            "role": "RICCARDO // INPUT",
            "text": cleanCommand,
            "accent": "#79AABD"
        })

        chatView.positionViewAtEnd()

        jarvisBridge.sendCommand(
            cleanCommand
        )
    }


    function memoryTypeColor(memoryType) {

        var type =
            memoryType.toLowerCase()

        if (type === "profile") {
            return "#00CFFF"
        }

        if (type === "preference") {
            return "#8B7CFF"
        }

        if (type === "project") {
            return "#00E59B"
        }

        if (type === "experience") {
            return "#FFC857"
        }

        return "#79AABD"
    }
}