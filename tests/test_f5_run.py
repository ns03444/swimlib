"""Unit tests for F5 run module."""

import pytest
import os
import json
from unittest.mock import Mock, patch, MagicMock
from swimlib.f5.run import (
    validate_target_software,
    validate_remote_connection,
    check_remote_storage,
    run_image_copy,
    run_image_stage,
    run_image_upgrade,
    PreValStatus
)


@patch("swimlib.f5.run.get_target_software")
def test_validate_target_software(mock_get_software):
    """Test validating and updating device with target software."""
    mock_get_software.return_value = {
        "target_version": "21.0.0",
        "artifacts": []
    }

    device = {"device_type_model": "BIG-IP Virtual Edition"}
    validate_target_software(device)

    assert device["target_version"] == "21.0.0"
    assert "artifacts" in device


@patch("swimlib.f5.run.SSHConnection")
def test_validate_remote_connection_success(mock_ssh_conn):
    """Test successful SSH connection validation."""
    mock_client = Mock()
    mock_ssh_conn.return_value.__enter__ = Mock(return_value=mock_client)
    mock_ssh_conn.return_value.__exit__ = Mock(return_value=False)

    device = {"device_address": "192.168.1.100"}
    result = validate_remote_connection(device, "admin", "password")

    assert result == mock_client


@patch("swimlib.f5.run.validate_remote_storage")
def test_check_remote_storage(mock_validate):
    """Test remote storage validation."""
    mock_ssh = Mock()
    device = {"remote_folder": "/shared/images"}

    check_remote_storage(mock_ssh, device)

    mock_validate.assert_called_once_with(mock_ssh, "/shared/images", min_gb=5)


@patch("swimlib.f5.run.sftp_copy_artifacts")
def test_run_image_copy(mock_sftp):
    """Test running image copy operation."""
    mock_ssh = Mock()
    device = {
        "artifacts": [{"local_path": "/local/file.iso"}],
        "remote_folder": "/shared/images"
    }

    run_image_copy(mock_ssh, device)

    mock_sftp.assert_called_once()


@patch("swimlib.f5.run.stage_artifacts")
def test_run_image_stage(mock_stage):
    """Test running image staging operation."""
    mock_ssh = Mock()
    device = {
        "artifacts": [{"remote_path": "/shared/file.iso"}],
        "target_version": "21.0.0"
    }

    run_image_stage(mock_ssh, device)

    mock_stage.assert_called_once_with(mock_ssh, device["artifacts"], "21.0.0")


@patch("swimlib.f5.run.upgrade_to_volume")
@patch("swimlib.f5.run.get_target_volume")
def test_run_image_upgrade(mock_get_volume, mock_upgrade):
    """Test running image upgrade operation."""
    mock_ssh = Mock()
    mock_get_volume.return_value = "HD1.2"
    device = {}

    run_image_upgrade(mock_ssh, device)

    mock_upgrade.assert_called_once_with(mock_ssh, "HD1.2")
