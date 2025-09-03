import pytest
from unittest.mock import MagicMock
from src.prism2.view_models.main_view_model import MainViewModel

@pytest.fixture
def mock_handler():
    """Fixture to create a mock HardwareHandler."""
    handler = MagicMock()
    handler.find_devices.return_value = ["USB-8451-0", "USB-8451-1"]
    handler.open_device.return_value = True
    handler.spi_transfer.return_value = b'\xCA\xFE'
    return handler

class MockTkVar:
    """A mock tkinter variable for testing ViewModels without a root window."""
    def __init__(self, value=None):
        self._value = value

    def get(self):
        return self._value

    def set(self, value):
        self._value = value

@pytest.fixture
def view_model(mocker, mock_handler):
    """Fixture to create a MainViewModel with a mocked HardwareHandler."""
    # Mock the HardwareHandler class to return our mock instance
    mocker.patch('src.prism2.view_models.main_view_model.HardwareHandler', return_value=mock_handler)

    # Mock the tkinter variable classes so we don't need a root window
    mocker.patch('src.prism2.view_models.main_view_model.ctk.Variable', new=lambda value=[]: MockTkVar(value))
    mocker.patch('src.prism2.view_models.main_view_model.ctk.StringVar', new=lambda value="": MockTkVar(value))
    mocker.patch('src.prism2.view_models.main_view_model.ctk.BooleanVar', new=lambda value=False: MockTkVar(value))

    vm = MainViewModel()

    # Since the VM is created after the mock is in place, it will use the mock
    return vm

def test_send_spi_command_updates_history(view_model):
    """
    Tests that sending an SPI command correctly updates the command history.
    """
    # Arrange
    # Connect the device first
    view_model.is_connected.set(True)
    command_to_send = "DEADBEEF"

    # Act
    view_model.send_spi_command(command_to_send)

    # Assert
    history = view_model.command_history.get()
    assert len(history) == 1
    assert history[0]["command"] == "DEADBEEF"
    assert history[0]["response"] == "CAFE" # from our mock handler

def test_initial_state(view_model, mock_handler):
    """
    Tests that the view model initializes correctly.
    """
    # Assert that find_devices was called on init
    mock_handler.find_devices.assert_called_once()

    # Assert that the device list and selected device are set
    assert view_model.device_list.get() == ["USB-8451-0", "USB-8451-1"]
    assert view_model.selected_device.get() == "USB-8451-0"
