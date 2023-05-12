# venus-os_ngrok - Easy external access, makes port externally reachable

<small>GitHub repository: [mr-manuel/venus-os_ngrok](https://github.com/mr-manuel/venus-os_ngrok)</small>

### Disclaimer

I wrote this script for myself. I'm not responsible, if you damage something using my script.


### Purpose

The allows you to access one selectable port from an external connection without the need to forward the port.

![venus-os](./screenshots/venus-os-services.png)

![venus-os](./screenshots/venus-os-ngrok.png)

### Installation

The driver can be installed via the [Setup Helper/Packet Manager](https://github.com/kwindrem/SetupHelper), by uploading it via SFTP to the directory `/data/venus-os_ngrok` and then running the `setup` file or by running this commands:

```bash
wget -O /tmp/venus-os_ngrok.zip https://github.com/mr-manuel/venus-os_ngrok/archive/refs/tags/latest.zip

unzip /tmp/venus-os_ngrok.zip -d /data

chmod +x /data/venus-os_ngrok/service/run /data/venus-os_ngrok/service/log/run /data/venus-os_ngrok/setup /data/venus-os_ngrok/venus-os_ngrok.py

bash /data/venus-os_ngrok/setup
```

⚠️ The [Setup Helper/Packet Manager](https://github.com/kwindrem/SetupHelper) is required for all installation methods.

The configuration is done via remote console/GUI.

### Config

Access to the remote console/GUI &rarr; Settings &rarr; Services &rarr; Ngrok



## Supporting/Sponsoring this project

You like the project and you want to support me?

[<img src="https://github.md0.eu/uploads/donate-button.svg" height="50">](https://www.paypal.com/donate/?hosted_button_id=3NEVZBDM5KABW)
