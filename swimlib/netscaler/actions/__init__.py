"""NetScaler Device Action Modules.

This package provides action modules for NetScaler (Citrix ADC) device operations,
including software transfer, installation, and upgrade workflows.

Modules:
    image_copy: SCP/SFTP transfer of software packages with SHA256 validation
    image_stage: Software installation to alternate partition
    image_upgrade: Device reboot to activate staged software
    config_backup: Configuration backup and validation operations
    ha_manager: High Availability pair coordination

Example:
    Complete NetScaler upgrade workflow::

        from swimlib.ssh_connect import SSHConnection
        from swimlib.netscaler.actions.image_copy import scp_copy_artifacts
        from swimlib.netscaler.actions.image_stage import stage_to_partition
        from swimlib.netscaler.actions.image_upgrade import upgrade_to_partition

        with SSHConnection("192.168.1.100", "nsroot", "password") as ssh:
            # Transfer artifacts
            scp_copy_artifacts(ssh, artifacts, "/var/nsinstall/")

            # Stage to alternate partition
            stage_to_partition(ssh, artifacts, target_version="14.1-25.109")

            # Activate upgrade (reboots device)
            upgrade_to_partition(ssh, partition=1)

.. versionadded:: 0.1.0
"""
