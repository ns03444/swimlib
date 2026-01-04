"""Image Staging Module for F5 BIG-IP Devices"""

from typing import List, Dict
import paramiko


class ImageStagingError(Exception):
    """Custom exception for image staging failures."""
    pass


def get_current_version(ssh_client: paramiko.SSHClient) -> str:
    """
    Get current running software version from F5 BIG-IP device.

    Args:
        ssh_client: Connected Paramiko SSHClient instance

    Returns:
        Current software version string

    Raises:
        ImageStagingError: If unable to retrieve version
    """
    try:
        cmd = "tmsh show sys version | grep Product | awk '{print $2}'"
        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        version = stdout.read().decode().strip()
        if not version:
            raise ImageStagingError("Unable to determine current version")
        return version
    except Exception as e:
        raise ImageStagingError(f"Failed to get current version: {e}") from e


def get_target_volume(ssh_client: paramiko.SSHClient) -> str:
    """
    Determine target volume for software installation.

    Args:
        ssh_client: Connected Paramiko SSHClient instance

    Returns:
        Target volume identifier (e.g., 'HD1.2', 'HD1.3')

    Raises:
        ImageStagingError: If unable to determine target volume
    """
    try:
        cmd = "tmsh show sys software status | grep -v yes | grep HD | head -1 | awk '{print $1}'"
        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        volume = stdout.read().decode().strip()
        if not volume:
            raise ImageStagingError("Unable to determine target volume")
        return volume
    except Exception as e:
        raise ImageStagingError(f"Failed to get target volume: {e}") from e


def stage_artifacts(ssh_client: paramiko.SSHClient, artifacts: List[Dict], target_version: str) -> None:
    """
    Stage software images on F5 BIG-IP device.

    Checks current version, determines target volume, and stages artifacts if needed.

    Args:
        ssh_client: Connected Paramiko SSHClient instance
        artifacts: List of artifact dicts with 'remote_path', 'filename'
        target_version: Expected software version to install

    Raises:
        ImageStagingError: If staging command fails
    """
    try:
        # Get current version and compare
        current_version = get_current_version(ssh_client)
        if current_version == target_version:
            return  # Already on target version, skip staging

        # Determine target volume
        target_volume = get_target_volume(ssh_client)

        # Stage each artifact
        for artifact in artifacts:
            remote_path = artifact["remote_path"]
            filename = artifact["filename"]

            # Execute tmsh install sys software image command
            cmd = f"tmsh install sys software image {remote_path} volume {target_volume}"
            stdin, stdout, stderr = ssh_client.exec_command(cmd)

            # Check for errors
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                error_output = stderr.read().decode().strip()
                raise ImageStagingError(f"Failed to stage {filename}: {error_output}")

    except ImageStagingError:
        raise
    except Exception as e:
        raise ImageStagingError(f"Image staging failed: {e}") from e
