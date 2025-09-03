class MockHardwareHandler:
    """
    A mock hardware handler that simulates the behavior of the real NI-845x
    hardware for development and testing purposes.
    """
    def __init__(self):
        self.is_open = False
        print("Initialized MockHardwareHandler.")

    def find_devices(self):
        """
        Returns a list with a single, simulated device name.
        """
        return ["SIM-845x"]

    def open_device(self, resource_name):
        """
        Simulates opening a device. Always succeeds.
        """
        print(f"Simulating opening device: {resource_name}")
        self.is_open = True
        return True

    def close_device(self):
        """
        Simulates closing the device.
        """
        print("Simulating closing device.")
        self.is_open = False

    def spi_transfer(self, data):
        """
        Simulates an SPI data transfer.

        For testing, this method returns a reversed copy of the data sent.
        For example, sending b'\\x01\\x02\\x03' will return b'\\x03\\x02\\x01'.

        Args:
            data (bytes): The data to "send".

        Returns:
            bytes: The simulated response data.
        """
        if not self.is_open:
            raise ConnectionError("No device is currently open.")

        print(f"Simulating SPI transfer with data: {data.hex().upper()}")

        # Reverse the bytes to simulate a response
        response = data[::-1]

        print(f"Simulated response: {response.hex().upper()}")
        return response
