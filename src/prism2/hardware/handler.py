from .ni845x import Ni845x, Ni845xError

class HardwareHandler:
    def __init__(self):
        self.device = None
        self.spi_config = None

    def find_devices(self):
        """
        Finds all connected NI-845x devices.

        Returns:
            A list of device resource names.
        """
        try:
            return Ni845x.find_devices()
        except Ni845xError as e:
            # In a real app, you'd want to log this error
            print(f"Error finding devices: {e}")
            return []

    def open_device(self, resource_name):
        """
        Opens a connection to the specified device.
        """
        try:
            self.device = Ni845x(resource_name)
            # You might want to set default IO voltage or timeout here
            return True
        except Ni845xError as e:
            print(f"Error opening device {resource_name}: {e}")
            self.device = None
            return False

    def close_device(self):
        """
        Closes the connection to the device.
        """
        if self.device:
            self.device.close()
            self.device = None

    def spi_transfer(self, data):
        """
        Sends and receives data over SPI.

        This is a placeholder. A real implementation would need to configure
        SPI settings (clock rate, etc.) before the transfer.
        """
        if not self.device:
            raise ConnectionError("No device is currently open.")

        # This is a simplified example. A full implementation would likely
        # create and configure an SpiConfiguration object.
        if self.spi_config is None:
            self.spi_config = self.device.create_spi_config()
            # Set default configuration here if needed
            # e.g., self.spi_config.set_clock_rate(1000)

        try:
            response = self.device.spi_write_read(self.spi_config, data)
            return response
        except Ni845xError as e:
            print(f"SPI transfer error: {e}")
            return None
