import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 480
    height: 320
    title: "HelloApp"

    Text {
        anchors.centerIn: parent
        text: "Hello World"
        font.pixelSize: 24
    }
}