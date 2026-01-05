"""SFTP Image Transfer Module"""

from typing import List, Dict
import paramiko


def compute_remote_md5(ssh_client: paramiko.SSHClient, remote_path: str) -> str:
    """Compute MD5 checksum of remote file."""
    stdin, stdout, stderr = ssh_client.exec_command(f"md5sum {remote_path}")
    return stdout.read().decode().strip().split()[0]


def sftp_copy_artifacts(ssh_client: paramiko.SSHClient, artifacts: List[Dict], remote_folder: str) -> None:
    """Copy artifacts to remote folder via SFTP with MD5 validation."""
    sftp = ssh_client.open_sftp()

    for artifact in artifacts:
        local_path = artifact["local_path"]
        remote_path = artifact["remote_path"]
        expected_md5 = artifact["md5"]

        # Skip if file exists with valid checksum
        try:
            sftp.stat(remote_path)
            if compute_remote_md5(ssh_client, remote_path) == expected_md5:
                continue
        except FileNotFoundError:
            pass

        # Transfer and validate
        sftp.put(local_path, remote_path)
        remote_md5 = compute_remote_md5(ssh_client, remote_path)
        assert remote_md5 == expected_md5, f"MD5 mismatch: {remote_path}"

    sftp.close()
