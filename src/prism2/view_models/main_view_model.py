import customtkinter as ctk
from ..hardware.handler import HardwareHandler
from ..protocol.parser import parse_hex_data

class MainViewModel:
    def __init__(self):
        """
        Initializes the MainViewModel.

        This class holds the application's state and business logic, and it
        interacts with the hardware handler.
        """
        self.hardware_handler = HardwareHandler()

        # --- State Variables ---
        # These are observable properties that the view can bind to.
        self.device_list = ctk.Variable(value=[])
        self.selected_device = ctk.StringVar()
        self.is_connected = ctk.BooleanVar(value=False)
        self.command_history = ctk.Variable(value=[])
        self.breakdown_text = ctk.StringVar()

        # --- Initial State ---
        self.refresh_devices()

    def refresh_devices(self):
        """
        Refreshes the list of available NI-845x devices.
        """
        print("Refreshing device list...")
        devices = self.hardware_handler.find_devices()
        self.device_list.set(devices)
        if devices:
            self.selected_device.set(devices[0])
        else:
            self.selected_device.set("")
        print(f"Found devices: {devices}")

    def connect_device(self):
        """
        Connects to the device specified in `selected_device`.
        """
        device_name = self.selected_device.get()
        if not device_name:
            print("No device selected.")
            return

        print(f"Connecting to {device_name}...")
        if self.hardware_handler.open_device(device_name):
            self.is_connected.set(True)
            print("Connection successful.")
        else:
            self.is_connected.set(False)
            print("Connection failed.")
            # In a real app, you might show an error message to the user here.

    def disconnect_device(self):
        """
        Disconnects from the currently connected device.
        """
        print("Disconnecting from device...")
        self.hardware_handler.close_device()
        self.is_connected.set(False)
        print("Device disconnected.")

    # --- SPI Command Methods ---

    def send_spi_command(self, command_hex):
        """
        Sends an SPI command to the connected device.

        Args:
            command_hex (str): The command to send, as a hex string.
        """
        if not self.is_connected.get():
            print("Cannot send command: No device connected.")
            return

        print(f"Sending SPI command: {command_hex}")

        try:
            # Convert hex string to bytes
            command_bytes = bytes.fromhex(command_hex)
        except ValueError:
            print(f"Invalid hex string: {command_hex}")
            # Optionally, update a status on the view model to show the error
            return

        response_bytes = self.hardware_handler.spi_transfer(command_bytes)

        if response_bytes is not None:
            response_hex = response_bytes.hex().upper()
            print(f"Received SPI response: {response_hex}")
            # Update the command history
            new_history = self.command_history.get()
            new_history.append({"command": command_hex, "response": response_hex})
            self.command_history.set(new_history)
        else:
            print("SPI transfer failed.")

    def select_history_item(self, item):
        """
        Parses a selected history item and updates the breakdown view.

        Args:
            item (dict): The selected history item, containing 'command' and 'response'.
        """
        cmd_breakdown = parse_hex_data(item['command'], is_command=True)
        rsp_breakdown = parse_hex_data(item['response'], is_command=False)

        full_breakdown = f"--- Command ---\n{cmd_breakdown}\n\n--- Response ---\n{rsp_breakdown}"

        self.breakdown_text.set(full_breakdown)