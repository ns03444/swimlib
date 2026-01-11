"""Unit tests for F5 pre-validation module."""

import pytest
import os
import tempfile
from unittest.mock import patch
from swimlib.f5.preval import get_target_software, SoftwareLookupException


def test_get_target_software_invalid_model():
    """Test software lookup with invalid device model."""
    with pytest.raises(SoftwareLookupException, match="not found in software matrix"):
        get_target_software("Invalid Model Name")


@patch("swimlib.f5.preval.software_matrix")
def test_get_target_software_missing_file(mock_matrix):
    """Test software lookup with missing local file."""
    mock_matrix.__contains__ = lambda self, key: True
    mock_matrix.__getitem__ = lambda self, key: {
        "target_version": "21.0.0",
        "artifacts": [
            {"local_path": "/nonexistent/path/file.iso", "md5": "abc123"}
        ]
    }

    with pytest.raises(SoftwareLookupException, match="Missing required image"):
        get_target_software("BIG-IP Virtual Edition")


@patch("swimlib.f5.preval.software_matrix")
def test_get_target_software_success(mock_matrix):
    """Test successful software lookup with existing files."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name

    try:
        mock_matrix.__contains__ = lambda self, key: True
        mock_matrix.__getitem__ = lambda self, key: {
            "target_version": "21.0.0",
            "artifacts": [
                {"local_path": tmp_path, "md5": "abc123"}
            ]
        }

        result = get_target_software("BIG-IP Virtual Edition")

        assert result["target_version"] == "21.0.0"
        assert len(result["artifacts"]) == 1
    finally:
        # Clean up temp file
        os.unlink(tmp_path)
