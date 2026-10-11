import QtQuick

QtObject {
    property real inputLevel: 0
    property real outputLevel: 0

    readonly property real activeLevel:
        Math.max(
            inputLevel,
            outputLevel
        )
}