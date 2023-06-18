import QtQuick 1.1
import com.victron.velib 1.0
import net.connman 0.1
import "utils.js" as Utils

MbPage {
	id: root
	title: qsTr("Services")

    //property VBusItem ngrok: VBusItem { bind: "com.victronenergy.settings/Settings/Services/Ngrok/Enabled" }

	model: VisualModels {
		VisualItemModel {
			MbSubMenu {
				description: qsTr("Modbus TCP")
				subpage: Component { PageSettingsModbusTcp {} }
				show: user.accessLevel >= User.AccessInstaller
				item {
					bind: "com.victronenergy.settings/Settings/Services/Modbus"
					text: item.value === 1 ? qsTr("Enabled") : qsTr("Disabled")
				}
			}

			MbSwitch {
				id: mqtt
				name: qsTr("MQTT on LAN (SSL)")
				bind: "com.victronenergy.settings/Settings/Services/MqttLocal"
			}

			MbSwitch {
				id: mqttLocalInsecure
				name: qsTr("MQTT on LAN (Plaintext)")
				bind: "com.victronenergy.settings/Settings/Services/MqttLocalInsecure"
				show: mqtt.checked
			}

			MbSubMenu {
				description: qsTr("Ngrok (Remote Port Forwarding/Access/Router)")
				//show: ngrok.valid
				subpage: Component { PageSettingsServicesNgrok {}  }
			}

			MbSwitch {
				name: qsTr("Console on VE.Direct 1")
				bind: "com.victronenergy.platform/Services/Console/Enabled"
				show: valid
				showAccessLevel: User.AccessSuperUser
			}
		}

		VisualDataModel {
			property VBusItem canInterface: VBusItem { bind: "com.victronenergy.platform/CanBus/Interfaces" }
			model: canInterface.value

			delegate: MbSubMenu {
				description: modelData["name"]
				subpage: Component {
					PageSettingsCanbus {
						title: modelData["name"]
						gateway: modelData["interface"]
						canConfig: modelData["config"]
					}
				}
			}
		}

		VisualItemModel {
			MbSwitch {
				name: "CAN-bus over tcp/ip (debug)"
				bind: "com.victronenergy.settings/Settings/Services/Socketcand"
				showAccessLevel: User.AccessService
			}
		}
	}
}