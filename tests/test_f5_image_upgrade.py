"""Unit tests for F5 image upgrade module."""

import pytest
from unittest.mock import Mock
from swimlib.f5.actions.image_upgrade import upgrade_to_volume


def test_upgrade_to_volume():
    """Test rebooting device to target volume."""
    mock_ssh = Mock()
    mock_stdout = Mock()
    mock_ssh.exec_command.return_value = (None, mock_stdout, None)

    upgrade_to_volume(mock_ssh, "HD1.2")

    mock_ssh.exec_command.assert_called_once_with("tmsh reboot volume HD1.2")
