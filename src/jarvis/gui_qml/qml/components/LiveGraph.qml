import QtQuick

Item {
    id: root

    property var values: []
    property color lineColor: "#00CFFF"
    property color fillColor: "#1400CFFF"
    property real maxValue: 100

    onValuesChanged: graph.requestPaint()
    onLineColorChanged: graph.requestPaint()

    Canvas {
        id: graph
        anchors.fill: parent

        onPaint: {
            var ctx = getContext("2d")
            ctx.reset()

            if (!root.values || root.values.length < 2)
                return

            var step = width / (root.values.length - 1)

            ctx.beginPath()

            for (var i = 0; i < root.values.length; i++) {
                var normalized =
                    Math.max(
                        0,
                        Math.min(
                            1,
                            root.values[i] / root.maxValue
                        )
                    )

                var x = i * step
                var y = height - normalized * height

                if (i === 0)
                    ctx.moveTo(x, y)
                else
                    ctx.lineTo(x, y)
            }

            ctx.strokeStyle = root.lineColor
            ctx.lineWidth = 1.5
            ctx.stroke()

            ctx.lineTo(width, height)
            ctx.lineTo(0, height)
            ctx.closePath()

            var gradient =
                ctx.createLinearGradient(
                    0,
                    0,
                    0,
                    height
                )

            gradient.addColorStop(
                0,
                Qt.rgba(
                    root.lineColor.r,
                    root.lineColor.g,
                    root.lineColor.b,
                    0.20
                )
            )

            gradient.addColorStop(
                1,
                Qt.rgba(
                    root.lineColor.r,
                    root.lineColor.g,
                    root.lineColor.b,
                    0.01
                )
            )

            ctx.fillStyle = gradient
            ctx.fill()
        }
    }
}