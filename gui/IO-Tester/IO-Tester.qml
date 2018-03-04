import QtQuick 2.0
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import Machinekit.Controls 1.0
import Machinekit.HalRemote.Controls 1.0
import Machinekit.HalRemote 1.0
import Machinekit.Service 1.0
import Machinekit.Application.Controls 1.0

ServiceWindow {
    id: main
    title: qsTr("IO Tester")

    // Services
    Service {
        id: halrcompService
        type: "halrcomp"
        required: true
    }

    Service {
        id: halrcmdService
        type: "halrcmd"
        required: true
    }

    HalRemoteComponent {
        property var pinsByName: { "0": "" }

        id: rcomp
        halrcmdUri: halrcmdService.uri
        halrcompUri: halrcompService.uri
        ready: connected || (halrcompService.ready && halrcmdService.ready)
        name: "io-control"
        create: false
        bind: false
        onErrorStringChanged: console.log(name + ': ' + errorString)

        function _getPins() {
            var pins = rcomp.pins;
            var pinMap = {};
            for (var i = 0; i < pins.length; ++i) {
                var id = pins[i].name;
                pinMap[id] = pins[i];
            }
            return pinMap;
        }

        onConnectedChanged: {
            if (connected) {
                rcomp.pinsByName = _getPins();
            }
            else {
                rcomp.pinsByName = {"0": "0"};
            }
        }
    }

    GridLayout {
        id: grid
        columns: 3
        anchors.fill: parent
        anchors.margins: 10
        Repeater {
            model: 34
            Button {
                id: button
                readonly property var pin: rcomp.pinsByName["io-%1.value".arg(index)]
                readonly property var idPin: rcomp.pinsByName["io-%1.pin".arg(index)]
                Layout.fillHeight: false
                text: "IO%1: pin %2".arg(index).arg(idPin ? idPin.value: 0)
                checkable: true

                Binding { target: pin; property: "value"; value: button.checked}
                Binding { target: button; property: "checked"; value: pin.value}
            }
        }
    }
}

