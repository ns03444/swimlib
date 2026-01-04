"""SFTP Image Transfer Module"""

from typing import List, Dict
import hashlib
import paramiko


class ImageTransferError(Exception):
    """Custom exception for image transfer failures."""
    pass


class ChecksumMismatchError(Exception):
    """Custom exception for MD5 checksum mismatches."""
    pass


def compute_remote_md5(ssh_client: paramiko.SSHClient, remote_path: str) -> str:
    """
    Compute MD5 checksum of remote file.

    Args:
        ssh_client: Connected Paramiko SSHClient instance
        remote_path: Path to remote file

    Returns:
        MD5 checksum as hex string
    """
    stdin, stdout, stderr = ssh_client.exec_command(f"md5sum {remote_path}")
    output = stdout.read().decode().strip()
    if not output:
        raise ChecksumMismatchError(f"Unable to compute MD5 for {remote_path}")
    return output.split()[0]


def sftp_copy_artifacts(ssh_client: paramiko.SSHClient, artifacts: List[Dict], remote_folder: str) -> None:
    """
    Copy artifacts to remote folder via SFTP if not already present, with MD5 validation.

    Args:
        ssh_client: Connected Paramiko SSHClient instance
        artifacts: List of artifact dicts with 'local_path', 'filename', 'remote_path', 'md5'
        remote_folder: Remote destination folder path

    Raises:
        ImageTransferError: If file transfer fails
        ChecksumMismatchError: If MD5 checksum validation fails
    """
    try:
        sftp = ssh_client.open_sftp()

        for artifact in artifacts:
            local_path = artifact["local_path"]
            remote_path = artifact["remote_path"]
            expected_md5 = artifact["md5"]

            # Check if file already exists on remote
            try:
                sftp.stat(remote_path)
                # File exists, validate checksum
                remote_md5 = compute_remote_md5(ssh_client, remote_path)
                if remote_md5 != expected_md5:
                    raise ChecksumMismatchError(
                        f"MD5 mismatch for {remote_path}: expected {expected_md5}, got {remote_md5}"
                    )
                continue  # File exists and checksum valid, skip
            except FileNotFoundError:
                pass  # File doesn't exist, proceed with copy

            # Transfer file
            sftp.put(local_path, remote_path)

            # Validate transferred file
            remote_md5 = compute_remote_md5(ssh_client, remote_path)
            if remote_md5 != expected_md5:
                raise ChecksumMismatchError(
                    f"MD5 mismatch after transfer for {remote_path}: expected {expected_md5}, got {remote_md5}"
                )

        sftp.close()

    except (ImageTransferError, ChecksumMismatchError):
        raise
    except Exception as e:
        raise ImageTransferError(f"SFTP transfer failed: {e}") from e
