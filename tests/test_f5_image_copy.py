"""Unit tests for F5 image copy module."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from swimlib.f5.actions.image_copy import compute_remote_md5, sftp_copy_artifacts


def test_compute_remote_md5():
    """Test MD5 checksum computation on remote device."""
    mock_ssh = Mock()
    mock_stdout = Mock()
    mock_stdout.read.return_value = b"abc123def456  /path/to/file.iso\n"
    mock_ssh.exec_command.return_value = (None, mock_stdout, None)

    result = compute_remote_md5(mock_ssh, "/path/to/file.iso")

    assert result == "abc123def456"
    mock_ssh.exec_command.assert_called_once_with("md5sum /path/to/file.iso")


def test_sftp_copy_artifacts_skip_existing():
    """Test SFTP copy skips files with valid checksums."""
    mock_ssh = Mock()
    mock_sftp = MagicMock()
    mock_ssh.open_sftp.return_value = mock_sftp

    # File exists and checksum matches
    mock_sftp.stat.return_value = True

    mock_stdout = Mock()
    mock_stdout.read.return_value = b"abc123  /remote/file.iso\n"
    mock_ssh.exec_command.return_value = (None, mock_stdout, None)

    artifacts = [
        {
            "local_path": "/local/file.iso",
            "remote_path": "/remote/file.iso",
            "md5": "abc123"
        }
    ]

    sftp_copy_artifacts(mock_ssh, artifacts, "/remote")

    # Should not call put since checksum matches
    mock_sftp.put.assert_not_called()
    mock_sftp.close.assert_called_once()


def test_sftp_copy_artifacts_transfers_new_file():
    """Test SFTP copy transfers files that don't exist."""
    mock_ssh = Mock()
    mock_sftp = MagicMock()
    mock_ssh.open_sftp.return_value = mock_sftp

    # File does not exist
    mock_sftp.stat.side_effect = FileNotFoundError()

    mock_stdout = Mock()
    mock_stdout.read.return_value = b"abc123  /remote/file.iso\n"
    mock_ssh.exec_command.return_value = (None, mock_stdout, None)

    artifacts = [
        {
            "local_path": "/local/file.iso",
            "remote_path": "/remote/file.iso",
            "md5": "abc123"
        }
    ]

    sftp_copy_artifacts(mock_ssh, artifacts, "/remote")

    # Should call put to transfer file
    mock_sftp.put.assert_called_once_with("/local/file.iso", "/remote/file.iso")
    mock_sftp.close.assert_called_once()
