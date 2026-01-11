"""Image Staging Module for F5 BIG-IP Software Installation.

This module provides functions for installing F5 BIG-IP software images to inactive volumes
on remote devices. It queries device state, determines target volumes, and executes the
TMSH install commands required for software staging.

Software staging is the process of installing new software to an inactive volume without
rebooting the device. The device continues running on its current volume while the new
software is prepared on an alternate volume.

Functions:
    get_current_version: Retrieve the currently running software version.
    get_target_volume: Determine which volume to use for software installation.
    stage_artifacts: Install software artifacts to the target volume.

Example:
    Stage software on an inactive volume::

        from swimlib.f5.actions.image_stage import stage_artifacts

        artifacts = [
            {"remote_path": "/shared/images/BIGIP-21.0.0.iso"}
        ]

        stage_artifacts(ssh_client, artifacts, target_version="21.0.0")
        print("Software staged successfully on inactive volume")

See Also:
    - :func:`swimlib.f5.actions.image_copy.sftp_copy_artifacts` for pre-stage file transfer
    - :func:`swimlib.f5.actions.image_upgrade.upgrade_to_volume` for post-stage reboot

.. versionadded:: 0.1.0
"""

from typing import List, Dict
import paramiko


def get_current_version(ssh_client: paramiko.SSHClient) -> str:
    """Retrieve the currently running software version from an F5 BIG-IP device.

    Executes the ``tmsh show sys version`` command and parses the output to extract
    the product version number.

    :param ssh_client: Connected paramiko SSHClient instance
    :type ssh_client: paramiko.SSHClient
    :return: Current software version string (e.g., "17.1.1")
    :rtype: str

    Example:
        Check current version before upgrade::

            from swimlib.f5.actions.image_stage import get_current_version

            current = get_current_version(ssh_client)
            print(f"Currently running: {current}")

            if current == target_version:
                print("Already on target version, skipping upgrade")

    Note:
        The parsing logic extracts the second field from the "Product" line using awk.

    .. versionadded:: 0.1.0
    """
    cmd = "tmsh show sys version | grep Product | awk '{print $2}'"
    stdin, stdout, stderr = ssh_client.exec_command(cmd)
    return stdout.read().decode().strip()


def get_target_volume(ssh_client: paramiko.SSHClient) -> str:
    """Determine the target volume for software installation on an F5 BIG-IP device.

    Queries the device's software status to find the first inactive volume. F5 BIG-IP
    devices typically have two volumes (HD1.1 and HD1.2). The device boots from one
    volume while the other remains inactive and available for software staging.

    :param ssh_client: Connected paramiko SSHClient instance
    :type ssh_client: paramiko.SSHClient
    :return: Inactive volume identifier (e.g., "HD1.2")
    :rtype: str

    Example:
        Identify target volume for installation::

            from swimlib.f5.actions.image_stage import get_target_volume

            target_vol = get_target_volume(ssh_client)
            print(f"Installing to volume: {target_vol}")

    Note:
        The query uses ``tmsh show sys software status`` and filters for volumes marked
        as inactive (not marked "yes" in the status output).

    .. versionadded:: 0.1.0
    """
    cmd = "tmsh show sys software status | grep -v yes | grep HD | head -1 | awk '{print $1}'"
    stdin, stdout, stderr = ssh_client.exec_command(cmd)
    return stdout.read().decode().strip()


def stage_artifacts(ssh_client: paramiko.SSHClient, artifacts: List[Dict], target_version: str) -> None:
    """Install software artifacts to the target volume on an F5 BIG-IP device.

    This function performs the software staging process by:
    1. Checking if the device is already running the target version (skip if true)
    2. Determining the target (inactive) volume
    3. Installing each artifact to the target volume using TMSH commands
    4. Waiting for each installation to complete before proceeding

    The installation does not reboot the device. The device continues running on its
    current volume. A separate reboot operation is required to activate the new software.

    :param ssh_client: Connected paramiko SSHClient instance
    :type ssh_client: paramiko.SSHClient
    :param artifacts: List of artifact dictionaries containing 'remote_path' for each image file
    :type artifacts: List[Dict[str, str]]
    :param target_version: Target software version string (e.g., "21.0.0")
    :type target_version: str

    Example:
        Stage multiple artifacts on inactive volume::

            artifacts = [
                {"remote_path": "/shared/images/BIGIP-21.0.0.ALL-FSOS.qcow2.zip"},
                {"remote_path": "/shared/images/Hotfix-BIGIP-21.0.0-ENG.iso"}
            ]

            stage_artifacts(ssh_client, artifacts, "21.0.0")
            print("Software staged - reboot required to activate")

    Note:
        Installation operations can take several minutes per artifact. The function
        waits for each install command to complete (channel.recv_exit_status()) before
        proceeding to the next artifact.

    Warning:
        If the device is already running the target version, this function returns
        immediately without performing any installation. This prevents redundant operations
        but may skip necessary reinstallations in some scenarios.

    See Also:
        - :func:`get_current_version` for version checking
        - :func:`get_target_volume` for volume selection
        - :func:`swimlib.f5.actions.image_upgrade.upgrade_to_volume` for reboot operation

    .. versionadded:: 0.1.0
    """
    # Skip if already on target version
    if get_current_version(ssh_client) == target_version:
        return

    target_volume = get_target_volume(ssh_client)

    for artifact in artifacts:
        cmd = f"tmsh install sys software image {artifact['remote_path']} volume {target_volume}"
        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        stdout.channel.recv_exit_status()  # Wait for completion
