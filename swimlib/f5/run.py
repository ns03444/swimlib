"""Software Upgrade Runner: Pre-validation Workflow"""
import os
import json
from enum import Enum
from typing import Dict

import paramiko
from swimlib.asdb import ASDBClient
from swimlib.f5.preval import get_target_software
from swimlib.ssh_connect import SSHConnection, SSHAuthError, validate_remote_storage
from swimlib.f5.actions.image_copy import sftp_copy_artifacts
from swimlib.f5.actions.image_stage import stage_artifacts, get_target_volume
from swimlib.f5.actions.image_upgrade import upgrade_to_volume


asdb = ASDBClient()


class PreValStatus(str, Enum):
    """Pre validation status values that map to icons."""
    PASS = "pass"
    FAIL = "fail"
    FAILAUTH = "fail_auth"
    IMAGE_MISSING = "image_missing"
    DISK_FULL = "disk_full"


def validate_target_software(device: Dict) -> None:
    """Validate and retrieve target software configuration for a device model."""
    try:
        device_model = device.get("device_type_model")
        artifacts = get_target_software(device_model)
        device.update(artifacts)
    except Exception as e:
        asdb.pre_validation_status(device, PreValStatus.IMAGE_MISSING)
        asdb.resolve_execution(f"error: Software lookup failed: {e}")

def validate_remote_connection(device: Dict, username: str, password: str) -> paramiko.SSHClient:
    """Establish and return an SSH connection to the remote device."""
    try:
        ip = device.get("device_address")
        with SSHConnection(ip, username, password) as ssh_client:
            return ssh_client
    except SSHAuthError as e:
        asdb.pre_validation_status(device, PreValStatus.FAILAUTH)
        asdb.resolve_execution(f"error: SSH authentication failed: {e}")
    except Exception as e:
        asdb.pre_validation_status(device, PreValStatus.FAIL)
        asdb.resolve_execution(f"error: SSH connection failed: {e}")

def check_remote_storage(ssh_client: paramiko.SSHClient, device: Dict) -> None:
    """Validate remote storage conditions on the device."""
    try:
        folder_path = device.get("remote_folder", "/shared/images")
        validate_remote_storage(ssh_client, folder_path, min_gb=5)

    except Exception as e:
        asdb.pre_validation_status(device, PreValStatus.DISK_FULL)
        asdb.resolve_execution(f"error: Remote storage validation failed: {e}")

def run_image_copy(ssh_client: paramiko.SSHClient, device: Dict) -> None:
    """Run the image copy process to transfer software artifacts to the device."""
    artifacts = device.get("artifacts", [])
    remote_folder = device.get("remote_folder", "/shared/images")

    try:
        sftp_copy_artifacts(ssh_client, artifacts, remote_folder)
    except Exception as e:
        asdb.pre_validation_status(device, PreValStatus.FAIL)
        asdb.resolve_execution(f"error: Image copy failed: {e}")

def run_image_stage(ssh_client: paramiko.SSHClient, device: Dict) -> None:
    """Run the image staging process to install software artifacts on the device."""
    artifacts = device.get("artifacts", [])
    target_version = device.get("target_version")

    try:
        stage_artifacts(ssh_client, artifacts, target_version)
    except Exception as e:
        asdb.pre_validation_status(device, PreValStatus.FAIL)
        asdb.resolve_execution(f"error: Image staging failed: {e}")

def run_image_upgrade(ssh_client: paramiko.SSHClient, device: Dict) -> None:
    """Run the image upgrade process to reboot device to target volume."""
    try:
        target_volume = get_target_volume(ssh_client)
        upgrade_to_volume(ssh_client, target_volume)
    except Exception as e:
        asdb.pre_validation_status(device, PreValStatus.FAIL)
        asdb.resolve_execution(f"error: Image upgrade failed: {e}")

def main():
    """Main workflow execution with execution_type control."""
    device = json.loads(os.getenv("SWIMLIB_DEVICE_JSON", "{}"))
    username = os.getenv("SWIMLIB_SSH_USERNAME", "admin")
    password = os.getenv("SWIMLIB_SSH_PASSWORD", "admin")
    execution_type = device.get("execution_type", "dry_run")

    # Always run pre-validation checks
    validate_target_software(device)
    ssh_client = validate_remote_connection(device, username, password)
    check_remote_storage(ssh_client, device)

    # Stop here if dry_run
    if execution_type == "dry_run":
        return

    # Run image copy for image_copy, image_stage, or image_upgrade
    if execution_type in ("image_copy", "image_stage", "image_upgrade"):
        run_image_copy(ssh_client, device)

    # Run image stage for image_stage or image_upgrade
    if execution_type in ("image_stage", "image_upgrade"):
        run_image_stage(ssh_client, device)

    # Run image upgrade only for image_upgrade
    if execution_type == "image_upgrade":
        run_image_upgrade(ssh_client, device)

if __name__ == "__main__":
    main()