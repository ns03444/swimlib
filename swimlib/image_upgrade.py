"""Image Upgrade Module for F5 BIG-IP Devices"""

import paramiko


def upgrade_to_volume(ssh_client: paramiko.SSHClient, target_volume: str) -> None:
    """Upgrade F5 BIG-IP device by rebooting to target volume."""
    cmd = f"tmsh reboot volume {target_volume}"
    stdin, stdout, stderr = ssh_client.exec_command(cmd)
