"""SFTP Image Transfer Module for F5 BIG-IP Software Artifacts.

This module provides functions for transferring F5 BIG-IP software images to remote devices
via SFTP with MD5 checksum validation to ensure file integrity.

The module implements intelligent transfer logic that skips files already present on the
remote system with valid checksums, optimizing transfer time for large image files.

Functions:
    compute_remote_md5: Calculate MD5 checksum of a file on the remote device.
    sftp_copy_artifacts: Transfer multiple software artifacts via SFTP with validation.

Example:
    Transfer software artifacts with checksum validation::

        from swimlib.ssh_connect import SSHConnection
        from swimlib.f5.actions.image_copy import sftp_copy_artifacts

        artifacts = [
            {
                "local_path": "/images/BIGIP-21.0.0.iso",
                "remote_path": "/shared/images/BIGIP-21.0.0.iso",
                "md5": "a1b2c3d4e5f678901234567890123456"
            }
        ]

        with SSHConnection("192.168.1.100", "admin", "password") as ssh:
            sftp_copy_artifacts(ssh, artifacts, "/shared/images")

See Also:
    - :mod:`swimlib.software_matrix` for artifact configurations
    - :func:`swimlib.f5.actions.image_stage.stage_artifacts` for post-transfer installation

.. versionadded:: 0.1.0
"""

from typing import List, Dict
import paramiko


def compute_remote_md5(ssh_client: paramiko.SSHClient, remote_path: str) -> str:
    """Compute MD5 checksum of a file on the remote F5 BIG-IP device.

    Executes the ``md5sum`` command on the remote device and parses the output to extract
    the MD5 hash value. This is used to verify file integrity after SFTP transfers.

    :param ssh_client: Connected paramiko SSHClient instance
    :type ssh_client: paramiko.SSHClient
    :param remote_path: Absolute path to the file on the remote device
    :type remote_path: str
    :return: 32-character hexadecimal MD5 checksum string
    :rtype: str

    Example:
        Verify checksum of a remote file::

            from swimlib.f5.actions.image_copy import compute_remote_md5

            md5 = compute_remote_md5(ssh_client, "/shared/images/BIGIP-21.0.0.iso")
            print(f"Remote MD5: {md5}")

            if md5 == "expected_checksum":
                print("Checksum verified!")

    Note:
        Assumes the remote system has the ``md5sum`` command available (standard on F5 BIG-IP).

    .. versionadded:: 0.1.0
    """
    stdin, stdout, stderr = ssh_client.exec_command(f"md5sum {remote_path}")
    return stdout.read().decode().strip().split()[0]


def sftp_copy_artifacts(ssh_client: paramiko.SSHClient, artifacts: List[Dict], remote_folder: str) -> None:
    """Copy software artifacts to remote device via SFTP with MD5 checksum validation.

    This function transfers multiple software artifacts (ISO files, qcow2 archives) to a
    remote F5 BIG-IP device using SFTP. It implements intelligent skip logic: if a file
    already exists on the remote system with a matching MD5 checksum, the transfer is skipped.

    For each artifact, the function:
    1. Checks if the file already exists remotely
    2. If it exists, verifies the MD5 checksum
    3. Skips transfer if checksum matches, otherwise proceeds
    4. Transfers the file via SFTP
    5. Validates the transferred file's checksum
    6. Raises AssertionError if validation fails

    :param ssh_client: Connected paramiko SSHClient instance for SFTP operations
    :type ssh_client: paramiko.SSHClient
    :param artifacts: List of artifact dictionaries, each containing 'local_path', 'remote_path', and 'md5' keys
    :type artifacts: List[Dict[str, str]]
    :param remote_folder: Remote folder path (for reference, not currently used in path construction)
    :type remote_folder: str
    :raises AssertionError: If post-transfer MD5 checksum does not match expected value
    :raises FileNotFoundError: If local artifact file does not exist

    Example:
        Transfer multiple artifacts with validation::

            artifacts = [
                {
                    "local_path": "/local/images/BIGIP-21.0.0.iso",
                    "remote_path": "/shared/images/BIGIP-21.0.0.iso",
                    "md5": "a1b2c3d4e5f678901234567890123456"
                },
                {
                    "local_path": "/local/images/Hotfix-BIGIP-21.0.0-ENG.iso",
                    "remote_path": "/shared/images/Hotfix-BIGIP-21.0.0-ENG.iso",
                    "md5": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7"
                }
            ]

            sftp_copy_artifacts(ssh_client, artifacts, "/shared/images")

    Note:
        Large ISO files (several GB) may take significant time to transfer. The skip
        logic prevents redundant transfers in retry scenarios.

    See Also:
        - :func:`compute_remote_md5` for checksum calculation
        - :func:`swimlib.f5.actions.image_stage.stage_artifacts` for post-copy installation

    .. versionadded:: 0.1.0
    """
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
