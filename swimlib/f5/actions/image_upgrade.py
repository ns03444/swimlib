"""Image Upgrade Module for F5 BIG-IP Device Reboots.

This module provides the final step in the F5 BIG-IP software upgrade workflow: rebooting
the device to activate software previously staged on an inactive volume.

After software has been copied and staged to an inactive volume, the device must reboot
to that volume to complete the upgrade process. This module executes the TMSH reboot command.

Functions:
    upgrade_to_volume: Reboot F5 BIG-IP device to a specified volume.

Example:
    Complete upgrade by rebooting to upgraded volume::

        from swimlib.f5.actions.image_upgrade import upgrade_to_volume
        from swimlib.f5.actions.image_stage import get_target_volume

        # Assume software already staged to HD1.2
        target_vol = get_target_volume(ssh_client)
        upgrade_to_volume(ssh_client, target_vol)
        print(f"Device rebooting to {target_vol}")

Warning:
    This operation reboots the device, causing service interruption. Ensure proper
    change management procedures are followed before executing upgrades in production.

See Also:
    - :func:`swimlib.f5.actions.image_stage.stage_artifacts` for pre-reboot software staging
    - :func:`swimlib.f5.actions.image_copy.sftp_copy_artifacts` for image transfer

.. versionadded:: 0.1.0
"""

import paramiko


def upgrade_to_volume(ssh_client: paramiko.SSHClient, target_volume: str) -> None:
    """Reboot an F5 BIG-IP device to activate software on the specified volume.

    Executes the ``tmsh reboot volume`` command to restart the device and boot from
    the specified volume. This is the final step in the upgrade workflow after software
    has been staged to an inactive volume.

    :param ssh_client: Connected paramiko SSHClient instance
    :type ssh_client: paramiko.SSHClient
    :param target_volume: Volume identifier to reboot into (e.g., "HD1.2")
    :type target_volume: str

    Example:
        Reboot to complete upgrade::

            from swimlib.f5.actions.image_upgrade import upgrade_to_volume

            # Reboot to previously staged volume
            upgrade_to_volume(ssh_client, "HD1.2")
            print("Reboot command sent - device will restart")

    Warning:
        This operation causes immediate device reboot and service disruption. The device
        will be unavailable during the reboot process (typically 5-15 minutes depending
        on platform and configuration).

        Ensure proper change management, maintenance windows, and rollback procedures
        are in place before executing this command in production environments.

    Note:
        The SSH connection will be terminated as the device reboots. The function does
        not wait for the reboot to complete or verify successful boot to the new volume.

    See Also:
        - :func:`swimlib.f5.actions.image_stage.get_target_volume` for volume selection
        - :func:`swimlib.f5.actions.image_stage.stage_artifacts` for pre-reboot installation

    .. versionadded:: 0.1.0
    """
    cmd = f"tmsh reboot volume {target_volume}"
    stdin, stdout, stderr = ssh_client.exec_command(cmd)
