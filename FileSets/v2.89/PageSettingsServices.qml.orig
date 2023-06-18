import QtQuick 1.1
import com.victron.velib 1.0
import net.connman 0.1
import "utils.js" as Utils

MbPage {
	id: root
	title: qsTr("Services")

	model: VisualItemModel {
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

		MbSwitch {
			name: qsTr("NMEA2000 on MQTT")
			bind: "com.victronenergy.settings/Settings/Services/MqttN2k"
			show: mqtt.checked && vePlatform.canInterfaces.length > 0 &&
				user.accessLevel >= User.AccessSuperUser
			backgroundColor: style.backgroundColorService
		}

		MbSwitch {
			name: qsTr("Console on VE.Direct 1")
			bind: "com.victronenergy.settings/Settings/Services/Console"
			showAccessLevel: User.AccessSuperUser
		}

		MbSubMenu {
			id: can1
			description: vePlatform.getCanBusName(0)
			subpage: Component {
				PageSettingsCanbus {
					title: can1.description
					gateway: vePlatform.canInterfaces.length > 0 ? vePlatform.canInterfaces[0] : ""
				}
			}
			show: vePlatform.canInterfaces.length > 0
		}

		MbSubMenu {
			id: can2
			description: vePlatform.getCanBusName(1)
			subpage: Component {
				PageSettingsCanbus {
					title: can2.description
					gateway: vePlatform.canInterfaces.length > 1 ? vePlatform.canInterfaces[1] : ""
				}
			}
			show: vePlatform.canInterfaces.length > 1
		}

		MbSwitch {
			name: "CAN-bus over tcp/ip (debug)"
			bind: "com.victronenergy.settings/Settings/Services/Socketcand"
			showAccessLevel: User.AccessService
		}
	}
}
