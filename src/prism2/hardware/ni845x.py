# -*- coding: utf-8 -*-
"""
Object-oriented Python ctypes wrapper for the National Instruments NI-845x driver DLL.

This module provides a more Pythonic interface to the ni845x.dll,
encapsulating handles and functions within classes for easier resource
management and a more intuitive programming experience.

Date: 2024-07-31
"""
import ctypes
import platform
import sys

# ==============================================================================
# Load Library
# ==============================================================================

# Determine the DLL name based on the operating system
# For simplicity, we assume 'ni845x.dll'. This might need adjustment
# based on the actual DLL name and location on the system.
_dll_name = 'Ni845x.dll'
_dll_loaded = False
ni845x_dll = None

try:
    # Use WinDLL for stdcall functions on Windows
    # The header defines NI845X_FUNC as __stdcall for WIN32 and __fastcall for WIN64
    # ctypes handles stdcall by default with WinDLL.
    # For fastcall on x64, stdcall is often sufficient as the first 4 args
    # are in registers, but ctypes handles this.
    if platform.system() == 'Windows':
        ni845x_dll = ctypes.WinDLL(_dll_name)
    else:
        # For other systems like Linux or macOS, use CDLL
        ni845x_dll = ctypes.CDLL(_dll_name)
    _dll_loaded = True
except OSError as e:
    print(f"Warning: Failed to load the ni845x library: {_dll_name}")
    print(f"         This is expected if the NI-845x driver is not installed.")
    print(f"         Application will run in a simulated mode without hardware access.")


# ==============================================================================
# Type Definitions from ni845x.h
# ==============================================================================
int8 = ctypes.c_char
uInt8 = ctypes.c_ubyte
int16 = ctypes.c_short
uInt16 = ctypes.c_ushort
int32 = ctypes.c_long
uInt32 = ctypes.c_ulong

# Define NiHandle based on architecture
if platform.architecture()[0] == '64bit':
    NiHandle = ctypes.c_ulonglong
else:
    NiHandle = ctypes.c_ulong

# Pointer types for convenience
puInt8 = ctypes.POINTER(uInt8)
puInt16 = ctypes.POINTER(uInt16)
puInt32 = ctypes.POINTER(uInt32)
pNiHandle = ctypes.POINTER(NiHandle)
pchar = ctypes.c_char_p
pint32 = ctypes.POINTER(int32)

# ==============================================================================
# Constants and Defines from ni845x.h
# ==============================================================================

# Status Codes
kNi845xErrorNoError = 0

# Generic Function Arguments
kNi845xOpenDrain = 0
kNi845xPushPull = 1

kNi845x33Volts = 33
kNi845x25Volts = 25
kNi845x18Volts = 18
kNi845x15Volts = 15
kNi845x12Volts = 12

# SPI Function Arguments
kNi845xSpiClockPolarityIdleLow = 0
kNi845xSpiClockPolarityIdleHigh = 1
kNi845xSpiClockPhaseFirstEdge = 0
kNi845xSpiClockPhaseSecondEdge = 1

# I2C Function Arguments
kNi845xI2cAddress7Bit = 0
kNi845xI2cAddress10Bit = 1
kNi845xI2cNakFalse = 0
kNi845xI2cNakTrue = 1

# DIO Function Arguments
kNi845xDioInput = 0
kNi845xDioOutput = 1
kNi845xDioLogicLow = 0
kNi845xDioLogicHigh = 1

# ==============================================================================
# Error Handling
# ==============================================================================

class Ni845xError(Exception):
    """Custom exception for NI-845x errors."""
    def __init__(self, error_code, function_name):
        self.error_code = error_code
        self.function_name = function_name
        self.message = self._get_error_string()
        super().__init__(f"Error in {self.function_name}: {self.message} (Code: {self.error_code})")

    def _get_error_string(self):
        """Retrieves the error description from the DLL."""
        # ni845xStatusToString function prototype
        _status_to_string = ni845x_dll.ni845xStatusToString
        _status_to_string.argtypes = [int32, uInt32, pchar]
        _status_to_string.restype = None # It's a void function

        # Create a buffer to hold the error string
        # 256 bytes should be sufficient for error messages
        buffer_size = 256
        error_buffer = ctypes.create_string_buffer(buffer_size)

        try:
            _status_to_string(self.error_code, buffer_size, error_buffer)
            return error_buffer.value.decode('utf-8')
        except Exception as e:
            return f"Failed to retrieve error string. Original exception: {e}"

def _check_error(status_code, func_name):
    """Checks the status code and raises an Ni845xError if it's not zero."""
    if status_code != kNi845xErrorNoError:
        raise Ni845xError(status_code, func_name)

# ==============================================================================
# Function Prototypes (argtypes and restype)
# ==============================================================================

if _dll_loaded:
    # Device Functions
    ni845x_dll.ni845xFindDevice.argtypes = [pchar, pNiHandle, puInt32]
    ni845x_dll.ni845xFindDevice.restype = int32

    ni845x_dll.ni845xFindDeviceNext.argtypes = [NiHandle, pchar]
    ni845x_dll.ni845xFindDeviceNext.restype = int32

    ni845x_dll.ni845xCloseFindDeviceHandle.argtypes = [NiHandle]
    ni845x_dll.ni845xCloseFindDeviceHandle.restype = int32

    ni845x_dll.ni845xOpen.argtypes = [pchar, pNiHandle]
    ni845x_dll.ni845xOpen.restype = int32

    ni845x_dll.ni845xClose.argtypes = [NiHandle]
    ni845x_dll.ni845xClose.restype = int32

    ni845x_dll.ni845xSetTimeout.argtypes = [NiHandle, uInt32]
    ni845x_dll.ni845xSetTimeout.restype = int32

    ni845x_dll.ni845xSetIoVoltageLevel.argtypes = [NiHandle, uInt8]
    ni845x_dll.ni845xSetIoVoltageLevel.restype = int32

    # SPI Basic API
    ni845x_dll.ni845xSpiConfigurationOpen.argtypes = [pNiHandle]
    ni845x_dll.ni845xSpiConfigurationOpen.restype = int32

    ni845x_dll.ni845xSpiConfigurationClose.argtypes = [NiHandle]
    ni845x_dll.ni845xSpiConfigurationClose.restype = int32

    ni845x_dll.ni845xSpiConfigurationSetClockRate.argtypes = [NiHandle, uInt16]
    ni845x_dll.ni845xSpiConfigurationSetClockRate.restype = int32

    ni845x_dll.ni845xSpiConfigurationSetChipSelect.argtypes = [NiHandle, uInt32]
    ni845x_dll.ni845xSpiConfigurationSetChipSelect.restype = int32

    ni845x_dll.ni845xSpiConfigurationSetPort.argtypes = [NiHandle, uInt8]
    ni845x_dll.ni845xSpiConfigurationSetPort.restype = int32

    ni845x_dll.ni845xSpiConfigurationSetClockPolarity.argtypes = [NiHandle, int32]
    ni845x_dll.ni845xSpiConfigurationSetClockPolarity.restype = int32

    ni845x_dll.ni845xSpiConfigurationSetClockPhase.argtypes = [NiHandle, int32]
    ni845x_dll.ni845xSpiConfigurationSetClockPhase.restype = int32

    ni845x_dll.ni845xSpiConfigurationSetNumBitsPerSample.argtypes = [NiHandle, uInt16]
    ni845x_dll.ni845xSpiConfigurationSetNumBitsPerSample.restype = int32

    ni845x_dll.ni845xSpiWriteRead.argtypes = [NiHandle, NiHandle, uInt32, puInt8, puInt32, puInt8]
    ni845x_dll.ni845xSpiWriteRead.restype = int32

    # DIO Functions
    ni845x_dll.ni845xDioSetPortLineDirectionMap.argtypes = [NiHandle, uInt8, uInt8]
    ni845x_dll.ni845xDioSetPortLineDirectionMap.restype = int32

    ni845x_dll.ni845xDioWritePort.argtypes = [NiHandle, uInt8, uInt8]
    ni845x_dll.ni845xDioWritePort.restype = int32

    ni845x_dll.ni845xDioReadPort.argtypes = [NiHandle, uInt8, puInt8]
    ni845x_dll.ni845xDioReadPort.restype = int32

    # I2C Functions
    ni845x_dll.ni845xI2cConfigurationOpen.argtypes = [pNiHandle]
    ni845x_dll.ni845xI2cConfigurationOpen.restype = int32

    ni845x_dll.ni845xI2cConfigurationClose.argtypes = [NiHandle]
    ni845x_dll.ni845xI2cConfigurationClose.restype = int32

    ni845x_dll.ni845xI2cWrite.argtypes = [NiHandle, NiHandle, uInt32, puInt8]
    ni845x_dll.ni845xI2cWrite.restype = int32

    ni845x_dll.ni845xI2cRead.argtypes = [NiHandle, NiHandle, uInt32, puInt32, puInt8]
    ni845x_dll.ni845xI2cRead.restype = int32

    # ... Add other function prototypes as needed ...

# ==============================================================================
# Object-Oriented Wrapper Classes
# ==============================================================================

class _HandleManager:
    """Base class to manage NI-845x handles and ensure they are closed."""
    def __init__(self, handle, close_func):
        self._handle = handle
        self._close_func = close_func
        self._closed = False

    def __del__(self):
        """Destructor to ensure the handle is closed."""
        self.close()

    def close(self):
        """Closes the handle."""
        if self._handle and not self._closed:
            status = self._close_func(self._handle)
            _check_error(status, self._close_func.__name__)
            self._handle = None
            self._closed = True

    @property
    def handle(self):
        if self._closed:
            raise Ni845xError(-1, "Handle is closed.")
        return self._handle


class SpiConfiguration(_HandleManager):
    """Manages an SPI Configuration session."""
    def __init__(self):
        """Opens a new SPI configuration handle."""
        handle = NiHandle()
        status = ni845x_dll.ni845xSpiConfigurationOpen(ctypes.byref(handle))
        _check_error(status, 'ni845xSpiConfigurationOpen')
        super().__init__(handle, ni845x_dll.ni845xSpiConfigurationClose)

    def set_clock_rate(self, rate_khz):
        """Sets the SPI clock rate in kHz."""
        status = ni845x_dll.ni845xSpiConfigurationSetClockRate(self.handle, uInt16(rate_khz))
        _check_error(status, 'ni845xSpiConfigurationSetClockRate')

    def set_chip_select(self, cs_line):
        """Sets the active chip select line."""
        status = ni845x_dll.ni845xSpiConfigurationSetChipSelect(self.handle, uInt32(cs_line))
        _check_error(status, 'ni845xSpiConfigurationSetChipSelect')

    def set_port(self, port_number):
        """Sets the SPI port number."""
        status = ni845x_dll.ni845xSpiConfigurationSetPort(self.handle, uInt8(port_number))
        _check_error(status, 'ni845xSpiConfigurationSetPort')

    def set_clock_polarity(self, polarity):
        """Sets the clock polarity (CPOL)."""
        status = ni845x_dll.ni845xSpiConfigurationSetClockPolarity(self.handle, int32(polarity))
        _check_error(status, 'ni845xSpiConfigurationSetClockPolarity')

    def set_clock_phase(self, phase):
        """Sets the clock phase (CPHA)."""
        status = ni845x_dll.ni845xSpiConfigurationSetClockPhase(self.handle, int32(phase))
        _check_error(status, 'ni845xSpiConfigurationSetClockPhase')

    def set_num_bits_per_sample(self, bits):
        """Sets the number of bits per sample."""
        status = ni845x_dll.ni845xSpiConfigurationSetNumBitsPerSample(self.handle, uInt16(bits))
        _check_error(status, 'ni845xSpiConfigurationSetNumBitsPerSample')


class I2cConfiguration(_HandleManager):
    """Manages an I2C Configuration session."""
    def __init__(self):
        """Opens a new I2C configuration handle."""
        handle = NiHandle()
        status = ni845x_dll.ni845xI2cConfigurationOpen(ctypes.byref(handle))
        _check_error(status, 'ni845xI2cConfigurationOpen')
        super().__init__(handle, ni845x_dll.ni845xI2cConfigurationClose)
   
    # Add I2C configuration methods here...


class Ni845x(_HandleManager):
    """Represents a single NI-845x device."""

    def __init__(self, resource_name):
        """
        Opens a session to an NI-845x device.

        Args:
            resource_name (str): The resource name of the device (e.g., "USB-8451").
        """
        if not _dll_loaded:
            raise Ni845xError(-1, "Cannot open device: NI-845x driver not loaded.")

        self.resource_name = resource_name.encode('utf-8')
        handle = NiHandle()
        status = ni845x_dll.ni845xOpen(self.resource_name, ctypes.byref(handle))
        _check_error(status, 'ni845xOpen')
        super().__init__(handle, ni845x_dll.ni845xClose)
        print(f"Successfully opened device: {resource_name}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @staticmethod
    def find_devices():
        """
        Finds all connected NI-845x devices.

        Returns:
            list: A list of resource names for all found devices.
        """
        if not _dll_loaded:
            return [] # Return empty list if library is not loaded

        find_handle = NiHandle()
        num_found = uInt32()
        # Max buffer size for a resource name
        buffer_size = 256
        first_device_buffer = ctypes.create_string_buffer(buffer_size)

        status = ni845x_dll.ni845xFindDevice(first_device_buffer, ctypes.byref(find_handle), ctypes.byref(num_found))
        _check_error(status, 'ni845xFindDevice')

        if num_found.value == 0:
            return []

        devices = [first_device_buffer.value.decode('utf-8')]
        for _ in range(num_found.value - 1):
            next_device_buffer = ctypes.create_string_buffer(buffer_size)
            status = ni845x_dll.ni845xFindDeviceNext(find_handle, next_device_buffer)
            _check_error(status, 'ni845xFindDeviceNext')
            devices.append(next_device_buffer.value.decode('utf-8'))
       
        # Close the find handle
        status = ni845x_dll.ni845xCloseFindDeviceHandle(find_handle)
        _check_error(status, 'ni845xCloseFindDeviceHandle')
       
        return devices

    def set_timeout(self, timeout_ms):
        """Sets the communication timeout in milliseconds."""
        status = ni845x_dll.ni845xSetTimeout(self.handle, uInt32(timeout_ms))
        _check_error(status, 'ni845xSetTimeout')

    def set_io_voltage_level(self, voltage_code):
        """Sets the IO voltage level (e.g., kNi845x33Volts)."""
        status = ni845x_dll.ni845xSetIoVoltageLevel(self.handle, uInt8(voltage_code))
        _check_error(status, 'ni845xSetIoVoltageLevel')

    # --- SPI Methods ---
    def create_spi_config(self):
        """Factory method to create an SPI configuration object."""
        return SpiConfiguration()

    def spi_write_read(self, config, write_data):
        """
        Performs an SPI write followed by a read.

        Args:
            config (SpiConfiguration): The SPI configuration object.
            write_data (bytes or list of int): The data to write.

        Returns:
            bytes: The data read from the SPI device.
        """
        write_size = len(write_data)
        write_buffer = (uInt8 * write_size)(*write_data)
       
        read_size = uInt32(write_size) # Typically read size is same as write size
        read_buffer = (uInt8 * write_size)()

        status = ni845x_dll.ni845xSpiWriteRead(
            self.handle,
            config.handle,
            uInt32(write_size),
            write_buffer,
            ctypes.byref(read_size),
            read_buffer
        )
        _check_error(status, 'ni845xSpiWriteRead')

        return bytes(read_buffer[:read_size.value])

    # --- I2C Methods ---
    def create_i2c_config(self):
        """Factory method to create an I2C configuration object."""
        return I2cConfiguration()

    def i2c_write(self, config, write_data):
        """Performs an I2C write."""
        write_size = len(write_data)
        write_buffer = (uInt8 * write_size)(*write_data)

        status = ni845x_dll.ni845xI2cWrite(
            self.handle,
            config.handle,
            uInt32(write_size),
            write_buffer
        )
        _check_error(status, 'ni845xI2cWrite')

    def i2c_read(self, config, num_bytes_to_read):
        """Performs an I2C read."""
        read_size = uInt32()
        read_buffer = (uInt8 * num_bytes_to_read)()

        status = ni845x_dll.ni845xI2cRead(
            self.handle,
            config.handle,
            uInt32(num_bytes_to_read),
            ctypes.byref(read_size),
            read_buffer
        )
        _check_error(status, 'ni845xI2cRead')
        return bytes(read_buffer[:read_size.value])


    # --- DIO Methods ---
    def dio_set_port_line_direction_map(self, port_number, direction_map):
        """
        Sets the direction for each line in a DIO port.

        Args:
            port_number (int): The DIO port number (0-7).
            direction_map (int): A bitmask where 1=output, 0=input.
        """
        status = ni845x_dll.ni845xDioSetPortLineDirectionMap(self.handle, uInt8(port_number), uInt8(direction_map))
        _check_error(status, 'ni845xDioSetPortLineDirectionMap')

    def dio_write_port(self, port_number, data):
        """Writes data to a DIO port."""
        status = ni845x_dll.ni845xDioWritePort(self.handle, uInt8(port_number), uInt8(data))
        _check_error(status, 'ni845xDioWritePort')

    def dio_read_port(self, port_number):
        """Reads data from a DIO port."""
        read_data = uInt8()
        status = ni845x_dll.ni845xDioReadPort(self.handle, uInt8(port_number), ctypes.byref(read_data))
        _check_error(status, 'ni845xDioReadPort')
        return read_data.value


# ==============================================================================
# Example Usage
# ==============================================================================
if __name__ == '__main__':
    if not _dll_loaded:
        print("Cannot run example: NI-845x library not loaded.")
        sys.exit(0)

    print("--- NI-845x Python Wrapper Example ---")

    try:
        # 1. Find available devices
        print("\nSearching for NI-845x devices...")
        devices = Ni845x.find_devices()
        if not devices:
            print("No NI-845x devices found. Please check your connection.")
            sys.exit(0)

        print(f"Found {len(devices)} device(s): {devices}")
        resource_name = devices[0]

        # 2. Open the first device found using a 'with' statement for automatic cleanup
        with Ni845x(resource_name) as device:
            print(f"\nSuccessfully opened a session to '{resource_name}'")

            # 3. Configure device properties
            device.set_timeout(5000)  # 5 second timeout
            print("Set timeout to 5000 ms")
           
            # Set I/O voltage to 3.3V
            device.set_io_voltage_level(kNi845x33Volts)
            print("Set IO Voltage to 3.3V")

            # 4. Perform an SPI transaction
            print("\n--- Performing SPI Write/Read ---")
            spi_config = device.create_spi_config()
           
            # Configure SPI parameters
            spi_config.set_port(0)
            spi_config.set_chip_select(0)
            spi_config.set_clock_rate(1000) # 1 MHz
            spi_config.set_clock_polarity(kNi845xSpiClockPolarityIdleLow)
            spi_config.set_clock_phase(kNi845xSpiClockPhaseFirstEdge)
            spi_config.set_num_bits_per_sample(8)
            print("SPI Configuration created and set.")

            # Data to send
            data_to_send = b'\xDE\xAD\xBE\xEF'
            print(f"Writing data: {list(data_to_send)}")

            # Perform the write/read
            read_data = device.spi_write_read(spi_config, data_to_send)
            print(f"Read data:    {list(read_data)}")

            # The spi_config handle will be closed automatically by its destructor
            spi_config.close()
            print("SPI Configuration closed.")

            # 5. Perform a DIO operation
            print("\n--- Performing DIO Write/Read ---")
            dio_port = 0
            # Set all lines of port 0 to output
            device.dio_set_port_line_direction_map(dio_port, 0xFF)
            print(f"Set DIO Port {dio_port} to all outputs.")
           
            # Write a value to the port
            device.dio_write_port(dio_port, 0xAA) # Write 10101010
            print(f"Wrote 0xAA to DIO Port {dio_port}.")

            # Set port to input to read back (if connected to another device)
            device.dio_set_port_line_direction_map(dio_port, 0x00)
            print(f"Set DIO Port {dio_port} to all inputs.")
           
            read_val = device.dio_read_port(dio_port)
            print(f"Read 0x{read_val:02X} from DIO Port {dio_port}.")


    except Ni845xError as e:
        print(f"\nAn NI-845x error occurred:")
        print(e)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

    print("\n--- Example Finished ---")