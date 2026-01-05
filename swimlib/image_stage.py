"""Image Staging Module for F5 BIG-IP Devices"""

from typing import List, Dict
import paramiko


def get_current_version(ssh_client: paramiko.SSHClient) -> str:
    """Get current running software version from F5 BIG-IP."""
    cmd = "tmsh show sys version | grep Product | awk '{print $2}'"
    stdin, stdout, stderr = ssh_client.exec_command(cmd)
    return stdout.read().decode().strip()


def get_target_volume(ssh_client: paramiko.SSHClient) -> str:
    """Determine target volume for software installation."""
    cmd = "tmsh show sys software status | grep -v yes | grep HD | head -1 | awk '{print $1}'"
    stdin, stdout, stderr = ssh_client.exec_command(cmd)
    return stdout.read().decode().strip()


def stage_artifacts(ssh_client: paramiko.SSHClient, artifacts: List[Dict], target_version: str) -> None:
    """Stage software images on F5 BIG-IP device."""
    # Skip if already on target version
    if get_current_version(ssh_client) == target_version:
        return

    target_volume = get_target_volume(ssh_client)

    for artifact in artifacts:
        cmd = f"tmsh install sys software image {artifact['remote_path']} volume {target_volume}"
        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        stdout.channel.recv_exit_status()  # Wait for completion
