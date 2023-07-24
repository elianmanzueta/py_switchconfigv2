from getpass import getpass
from netmiko import (
    ConnectHandler,
    SSHDetect,
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)
import textfsm
import argparse
from argparse import RawTextHelpFormatter


class Switch:
    """
    The Switch() class initializes an object that holds the required parameters
    to connect, disconnect, and send commands to a network device using netmiko.
    """

    def __init__(self, ip: str, username: str, password: str):
        self.ip = ip
        self.username = username
        self.password = password
        self.connection = None
        self.match = None
        self.host = None

    def connect(self) -> bool:
        """
        Connect to a given network device.
        """
        device = {
            "device_type": "autodetect",
            "host": self.ip,
            "username": self.username,
            "password": self.password,
        }

        # Auto-detect device type (IOS/NXOS)
        print("Guessing device type...")
        try:
            guess = SSHDetect(**device)
        except TimeoutError:
            print(f"Connection to {self.ip} has timed out.")
        except NetmikoTimeoutException:
            print(f"Connection to {self.ip} has timed out.")
        except NetmikoAuthenticationException:
            print(f"Authentication failed on {self.ip}")
        else:
            self.match = guess.autodetect()
            device["device_type"] = self.match
            print(f"Device type found: {self.match}")
            self.connection = ConnectHandler(**device)
            # Prints out hostname of the device you're connected to
            if self.connection and self.match:
                self.host = self.connection.find_prompt()[:-1]
                print(f"Connected to: {self.host} on {self.ip}.\n")
                return True
            else:
                print("Device connection has not been established.")
                return None

    def disconnect(self) -> None:
        """
        Disconnects from the device.
        """
        if self.connection:
            self.connection.disconnect()
            print(f"\nDisconnected from {self.host}.")
            self.connection = None

    def send_command(self, command: str) -> str:
        """
        Sends a command to the network device.
        """
        if self.connection:
            output = self.connection.send_command(command)
            return output
        else:
            print("\nDevice connection has not been established.")

    def send_command_list(self, command: list) -> str:
        """
        Sends a list of commands to a network device.
        """
        if self.connection:
            output = self.connection.send_config_set(command)
            return output
        else:
            print("\nDevice connection has not been established.")


def access_config(interface: str, vlan: list):
    if switch.connection:
        commands = [
            f"interface {interface}",
            "switchport mode access",
            f"switchport access vlan {vlan[0]}",
        ]
        switch.send_command_list(commands)
        print(f"Configuration successful.\n")
        switch.send_command(f"show run | sec interface {interface}")


def trunk_config(interface: str, vlan: list):
    if switch.connection:
        commands = [
            f"interface {interface}",
            "switchport mode trunk",
            "switchport trunk encap dot1q",
            "swoitchport trunk vlan allowed none",
            f"switchport trunk vlan allowed {', '.join(vlan)}",
        ]
        switch.send_command_list(commands)
        print(f"Configuration successful.\n")
        switch.send_command(f"show run | sec interface {interface}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Configures a switchport as an access or trunk port and assigns VLANs to it.",
        formatter_class=RawTextHelpFormatter,
    )

    parser.add_argument(
        "-ip", "--ipaddress", help="IP Address", type=str, required=True
    )
    parser.add_argument("-user", "--username", help="Username", type=str, required=True)
    parser.add_argument(
        "-m",
        "--mode",
        help="Switchport mode (Access/Trunk)",
        choices=("Access", "Trunk"),
        type=str,
        action="store_true",
        required=True,
    )
    parser.add_argument("-v", "--vlans", help="VLANs", type=str, required=True)
    parser.add_argument("-interface", help="Interface", type=str, required=True)

    args = parser.parse_args()

    ipaddress = args.ipaddress
    username = args.username
    switchmode = args.mode
    vlans = args.vlans
    interface = args.interface

    if ipaddress and username:
        password = getpass()

        switch = Switch(ipaddress, username, password)
        print(f"Connecting to {switch.host} on {switch.ip}...\n")
        switch.connect()

        print(
            "\nMake sure to not have spaces if you are adding multiple VLANs. Ex. (10,20,30,40)"
        )

        if switch.connection:
            vlan_list = vlans.split(",")
            if switchmode == "Access" and interface:
                access_config(interface, vlans[0])
            if switchmode == "Trunk" and interface:
                trunk_config(interface, vlans)
        else:
            parser.print_help()
