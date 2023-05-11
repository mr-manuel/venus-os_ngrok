import QtQuick 1.1
import com.victron.velib 1.0
import "utils.js" as Utils

MbPage {
	id: root
	title: qsTr("Ngrok (Make port externally reachable)")

	property VBusItem authtoken: VBusItem { bind: "com.victronenergy.settings/Settings/Services/Ngrok/AuthToken" }

	model: VisibleItemModel {

		MbSwitch {
			id: ngrok
			name: qsTr("Start ngrok")
			enabled: authtoken.value != ""
			bind: "com.victronenergy.settings/Settings/Services/Ngrok/Enabled"
		}

		MbEditBoxAuthToken {
			description: qsTr("Your Authtoken")
			readonly: ngrok.checked
			item.bind: "com.victronenergy.settings/Settings/Services/Ngrok/AuthToken"
			maximumLength: 64
			enableSpaceBar: false
			backgroundColor: authtoken.value == "" ? "#ff0000" : "#ddd"
			wrapMode: Text.Wrap
		}

		MbItemText {
			text: qsTr("You have first to create a free account at ngrok.com. After logging in you find your authtoken under \"Getting Started\" --> \"Your Authtoken\" or https://dashboard.ngrok.com/get-started/your-authtoken")
			wrapMode: Text.WordWrap
			show: authtoken.value == "" && ngrok.checked == false
		}

		MbItemOptions {
			description: qsTr("Protocol")
			readonly: authtoken.value == "" || ngrok.checked
			bind: "com.victronenergy.settings/Settings/Services/Ngrok/Protocol"
			possibleValues:[
				MbOption{description: qsTr("TCP"); value: "tcp"},
				MbOption{description: qsTr("HTTP"); value: "http"},
				MbOption{description: qsTr("HTTPS"); value: "https"}
			]
		}

		MbEditBox {
			id: port
			description: qsTr("Port to forward")
			readonly: authtoken.value == "" || ngrok.checked
			item.bind: "com.victronenergy.settings/Settings/Services/Ngrok/PortToForward"
			maximumLength: 5
			enableSpaceBar: true
		}

		MbItemValue {
			description: qsTr("Port reachable at")
			show: ngrok.checked
			item.bind: "com.victronenergy.settings/Settings/Services/Ngrok/Link"
		}

	}
}
