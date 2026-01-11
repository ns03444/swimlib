"""Unit tests for F5 image stage module."""

import pytest
from unittest.mock import Mock
from swimlib.f5.actions.image_stage import get_current_version, get_target_volume, stage_artifacts


def test_get_current_version():
    """Test retrieving current version from device."""
    mock_ssh = Mock()
    mock_stdout = Mock()
    mock_stdout.read.return_value = b"17.1.1\n"
    mock_ssh.exec_command.return_value = (None, mock_stdout, None)

    result = get_current_version(mock_ssh)

    assert result == "17.1.1"
    mock_ssh.exec_command.assert_called_once()


def test_get_target_volume():
    """Test determining target volume for installation."""
    mock_ssh = Mock()
    mock_stdout = Mock()
    mock_stdout.read.return_value = b"HD1.2\n"
    mock_ssh.exec_command.return_value = (None, mock_stdout, None)

    result = get_target_volume(mock_ssh)

    assert result == "HD1.2"
    mock_ssh.exec_command.assert_called_once()


def test_stage_artifacts_skips_if_already_on_target():
    """Test staging skips if device is already on target version."""
    mock_ssh = Mock()
    mock_stdout = Mock()
    mock_stdout.read.return_value = b"21.0.0\n"
    mock_ssh.exec_command.return_value = (None, mock_stdout, None)

    artifacts = [
        {"remote_path": "/shared/images/BIGIP-21.0.0.iso"}
    ]

    stage_artifacts(mock_ssh, artifacts, "21.0.0")

    # Should only call exec_command once for version check
    assert mock_ssh.exec_command.call_count == 1


def test_stage_artifacts_installs_to_target_volume():
    """Test staging installs artifacts to target volume."""
    mock_ssh = Mock()

    # First call returns current version, second returns target volume
    mock_stdout1 = Mock()
    mock_stdout1.read.return_value = b"17.1.1\n"
    mock_stdout2 = Mock()
    mock_stdout2.read.return_value = b"HD1.2\n"
    mock_stdout3 = Mock()
    mock_stdout3.channel.recv_exit_status.return_value = 0

    mock_ssh.exec_command.side_effect = [
        (None, mock_stdout1, None),  # get_current_version
        (None, mock_stdout2, None),  # get_target_volume
        (None, mock_stdout3, None),  # install command
    ]

    artifacts = [
        {"remote_path": "/shared/images/BIGIP-21.0.0.iso"}
    ]

    stage_artifacts(mock_ssh, artifacts, "21.0.0")

    # Should call exec_command for version, volume, and install
    assert mock_ssh.exec_command.call_count == 3
