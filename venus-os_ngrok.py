#!/usr/bin/env python

# This program creates and monitors a dBus service to trigger a system shutdown
# The com.victronenergy.shutdown service is created and contains one parameter: /Shutdown
# /Shutdown is normally 0 but if this program detects a value other than 0,
# the system shutdown -h now call is made

# it also reads a GPIO pin on Raspberry Pi platforms
#    if that pin goes low the system is a shutdown
#    a switch in Settings enables this input so it doesn't cause unintended shutdowns
#

from subprocess import check_output, CalledProcessError

# import subprocess
from time import sleep

# import platform
# import argparse
import logging
import sys
import os

# import time
import dbus  # pyright: ignore[reportMissingImports]

# accommodate both Python 2 and 3
# if the Python 3 GLib import fails, import the Python 2 gobject
try:
    from gi.repository import GLib  # pyright: ignore[reportMissingImports] for Python 3
except ImportError:
    import gobject as GLib  # pyright: ignore[reportMissingImports] for Python 2

# add the path to our own packages for import
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "ext", "velib_python"))
from vedbus import VeDbusService
from settingsdevice import SettingsDevice


# set logging level to include info level entries
logging.basicConfig(level=logging.INFO)


ShutdownServiceName = "com.victronenergy.ngrok"

# These methods permit creation of a separate connection for each Repeater
# overcoming the one service per process limitation
# requires updated vedbus, originally obtained from https://github.com/victronenergy/dbus-digitalinputs
# updates are incorporated in the ext directory of this package


class SystemBus(dbus.bus.BusConnection):
    def __new__(cls):
        return dbus.bus.BusConnection.__new__(cls, dbus.bus.BusConnection.TYPE_SYSTEM)


class SessionBus(dbus.bus.BusConnection):
    def __new__(cls):
        return dbus.bus.BusConnection.__new__(cls, dbus.bus.BusConnection.TYPE_SESSION)


def dbusconnection():
    return SessionBus() if "DBUS_SESSION_BUS_ADDRESS" in os.environ else SystemBus()


def getResponse(command):
    try:
        result = check_output(command, shell=True).decode()
        return result.replace("\n", "")
    except CalledProcessError:
        return False
    except Exception:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        file = exception_traceback.tb_frame.f_code.co_filename
        line = exception_traceback.tb_lineno
        logging.error(
            f"Exception occurred: {repr(exception_object)} of type {exception_type} in {file} line #{line}"
        )
        return False


class Monitor:
    DbusService = None
    DbusBus = None

    enabled = None
    authtoken = None
    protocol = None
    porttoforward = None
    link = None

    def __init__(self):
        # set up unique dBus connection and dBus service
        self.DbusBus = dbusconnection()
        self._createDbusService()

        GLib.timeout_add(1000, self._background)
        return None

    # flag value change from external source
    def _handlechangedvalue(self, path, value):
        # if value == 1:
        #    logging.info("User shutdown received from GUI - shutting down system")
        #    os.system("shutdown -h now")
        logging.error(
            "_handlechangedvalue -_> path: " + str(path) + " - value: " + str(value)
        )
        return True

    def _background(self):
        # if shutdown pin is enabled in the GUI and a transition to active just occurred, trigger shutdown
        if self.enabled != self.DbusSettings["Enabled"]:
            logging.info(
                'Value "Enabled" changed from "'
                + str(self.enabled)
                + '" to "'
                + str(self.DbusSettings["Enabled"])
                + '"'
            )

            pid = getResponse("pidof /data/venus-os_ngrok/ngrok")
            logging.info("pid: " + str(pid))

            if self.DbusSettings["Enabled"] == 1:
                if pid is False:
                    logging.info(
                        "Start ngrok ("
                        + self.DbusSettings["Protocol"]
                        + "/"
                        + str(self.DbusSettings["PortToForward"])
                        + ")..."
                    )

                    # ngrok tcp 22
                    # ngrok http 80
                    # ngrok http https://localhost:1881
                    protocol = (
                        "http"
                        if self.DbusSettings["Protocol"] == "https"
                        else self.DbusSettings["Protocol"]
                    )
                    port = (
                        "https://localhost:" + str(self.DbusSettings["PortToForward"])
                        if self.DbusSettings["Protocol"] == "https"
                        else str(self.DbusSettings["PortToForward"])
                    )
                    command = (
                        "nohup /data/venus-os_ngrok/ngrok "
                        + protocol
                        + " "
                        + port
                        + " --log=false > /tmp/ngrok.out &"
                        # + " --log=stdout > /tmp/ngrok.out &"
                        # + " --log=stderr > /tmp/ngrok.out &"
                    )
                    logging.info(command)

                    try:
                        os.system(command)
                        pid = getResponse("pidof /data/venus-os_ngrok/ngrok")
                        url = False
                        count = 0
                        while url is False:
                            url = getResponse(
                                'curl -s http://localhost:4040/api/tunnels | grep -o \'"public_url":"[^"]*\' | grep -o \'[^"]*$\''
                            )
                            sleep(1)
                            count += 1
                            logging.debug("sleep: " + str(count))
                            if count >= 10:
                                url = getResponse(
                                    "tail -n 20 /var/log/venus-os_ngrok/current | grep ERR_NGROK | tail -n 1 | tai64nlocal"
                                )[30::]
                                logging.error(url)
                                break

                    except Exception:
                        (
                            exception_type,
                            exception_object,
                            exception_traceback,
                        ) = sys.exc_info()
                        file = exception_traceback.tb_frame.f_code.co_filename
                        line = exception_traceback.tb_lineno
                        err = f"Exception occurred: {repr(exception_object)} of type {exception_type} in {file} line #{line}"
                        logging.error(err)
                        url = err

                    self.DbusSettings["Link"] = url
                    logging.info("pid: " + str(pid) + " - url: " + str(url))
                else:
                    logging.info("already running with pid: " + str(pid))

            elif pid:
                logging.info("Stopping ngrok...")
                # pid = getResponse("pidof ngrok")
                # if not pid:
                os.system('pkill -f "/data/venus-os_ngrok/ngrok"')
                self.DbusSettings["Link"] = ""
            else:
                logging.info("ngrok was not running")
                self.DbusSettings["Link"] = ""

            self.enabled = self.DbusSettings["Enabled"]

        if self.authtoken != self.DbusSettings["AuthToken"]:
            logging.info(
                'Value "AuthToken" changed from "'
                + str(self.authtoken)
                + '" to "'
                + str(self.DbusSettings["AuthToken"])
                + '"'
            )

            try:
                os.system(
                    "/data/venus-os_ngrok/ngrok config add-authtoken "
                    + self.DbusSettings["AuthToken"]
                )
            except Exception as e:
                logging.error("Unexpected error: " + str(e))

            self.authtoken = self.DbusSettings["AuthToken"]

        if self.protocol != self.DbusSettings["Protocol"]:
            logging.info(
                'Value "Protocol" changed from "'
                + str(self.protocol)
                + '" to "'
                + str(self.DbusSettings["Protocol"])
                + '"'
            )
            self.protocol = self.DbusSettings["Protocol"]

        if self.porttoforward != self.DbusSettings["PortToForward"]:
            logging.info(
                'Value "PortToForward" changed from "'
                + str(self.porttoforward)
                + '" to "'
                + str(self.DbusSettings["PortToForward"])
                + '"'
            )
            self.porttoforward = self.DbusSettings["PortToForward"]

        return True

    def _createDbusService(self):
        # updated version of VeDbusService (in ext directory) -- see https://github.com/victronenergy/dbus-digitalinputs for new imports
        self.DbusService = VeDbusService(ShutdownServiceName, bus=self.DbusBus)

        # Create the objects

        self.DbusService.add_path("/Mgmt/ProcessName", __file__)
        self.DbusService.add_path("/Mgmt/ProcessVersion", "1.0")
        self.DbusService.add_path("/Mgmt/Connection", "dbus")

        self.DbusService.add_path("/DeviceInstance", 0)
        self.DbusService.add_path("/ProductName", "Ngrok")
        self.DbusService.add_path("/ProductId", 0x0)
        self.DbusService.add_path("/FirmwareVersion", "v0.0.1")
        # self.DbusService.add_path("/HardwareVersion", 0)
        # self.DbusService.add_path("/Serial", "")
        # use numeric values (1/0) not True/False for /Connected to make GUI display correct state
        self.DbusService.add_path("/Connected", 1)
        # indicates to the GUI that it can show the RPI shutdown pin control
        # self.DbusService.add_path("/ExtShutdownPresent", 0)

        # GUI sets this to initialte shutdown
        self.DbusService.add_path(
            "/Shutdown", 0, writeable=True, onchangecallback=self._handlechangedvalue
        )

        # create the setting that allows enabling the RPI shutdown pin
        settingsList = {
            "Enabled": ["/Settings/Services/Ngrok/Enabled", 0, 0, 1],
            "AuthToken": ["/Settings/Services/Ngrok/AuthToken", "", 0, 64],
            "Protocol": ["/Settings/Services/Ngrok/Protocol", "tcp", 0, 16],
            "PortToForward": ["/Settings/Services/Ngrok/PortToForward", 22, 0, 65536],
            "Link": ["/Settings/Services/Ngrok/Link", "", 0, 128],
        }
        self.DbusSettings = SettingsDevice(
            bus=dbus.SystemBus(),
            supportedSettings=settingsList,
            timeout=10,
            eventCallback=None,
        )

        # self.enabled = self.DbusSettings["Enabled"]
        self.authtoken = self.DbusSettings["AuthToken"]
        self.protocol = self.DbusSettings["Protocol"]
        self.porttoforward = self.DbusSettings["PortToForward"]
        # self.link = self.DbusSettings["Link"]

        # enable the shutdown pin only if on a Raspberry PI
        # if self.ShutdownPinPresent:
        #    self.DbusService["/ExtShutdownPresent"] = 1

        return


def main():
    from dbus.mainloop.glib import (  # pyright: ignore[reportMissingImports]
        DBusGMainLoop,
    )

    global TheBus

    # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
    DBusGMainLoop(set_as_default=True)

    logging.info("*** Ngrok Starting ***")

    Monitor()

    mainloop = GLib.MainLoop()
    mainloop.run()


# Always run our main loop so we can process updates
main()
