import QtQuick 1.1
import com.victron.velib 1.0
import "utils.js" as Utils

MbPage {
	id: root
	title: qsTr("Ngrok")

////// GuiMods — DarkMode
	property VBusItem darkModeItem: VBusItem { bind: "com.victronenergy.settings/Settings/GuiMods/DarkMode" }
	property bool darkMode: darkModeItem.valid && darkModeItem.value == 1

	property VBusItem authtoken: VBusItem { bind: "com.victronenergy.settings/Settings/Services/Ngrok/AuthToken" }

	model: VisibleItemModel {

		MbSwitch {
			id: ngrok
			name: qsTr("Start ngrok")
			enabled: authtoken.value != ""
			bind: "com.victronenergy.settings/Settings/Services/Ngrok/Enabled"
		}

		MbItemValue {
			description: qsTr("Port reachable at")
			show: ngrok.checked
			item.bind: "com.victronenergy.settings/Settings/Services/Ngrok/Link"
		}

		MbEditBoxAuthToken {
			description: qsTr("Your Authtoken")
			readonly: ngrok.checked
			item.bind: "com.victronenergy.settings/Settings/Services/Ngrok/AuthToken"
			maximumLength: 50
			enableSpaceBar: false
			backgroundColor: authtoken.value == "" ? "#ff0000" : (!darkMode ? "#ddd" : "#4b4b4b")
			//wrapMode: Text.Wrap
		}

		MbItemText {
			text: qsTr("You have first to create a free account at ngrok.com. After logging in you find your authtoken under \"Getting Started\" --> \"Your Authtoken\" or https://dashboard.ngrok.com/get-started/your-authtoken")
			wrapMode: Text.WordWrap
			show: authtoken.value == "" && ngrok.checked == false
		}

		MbItemOptions {
			id: protocol
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

		MbEditBoxAuthToken {
			description: qsTr("Custom NGROK Domain for HTTP/HTTPS (optional)")
			readonly: ngrok.checked
			item.bind: "com.victronenergy.settings/Settings/Services/Ngrok/CustomDomain"
			maximumLength: 50
			enableSpaceBar: false
			backgroundColor: !darkMode ? "#ddd" : "#4b4b4b"
			show: protocol.value == "http" || protocol.value == "https"
		}

	}
}
