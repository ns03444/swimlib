"""Palo Alto Networks Platform Module.

This package provides automation capabilities for Palo Alto Networks next-generation
firewalls (PAN-OS devices), including software upgrades, configuration management,
and High Availability orchestration.

Modules:
    run: Main workflow orchestration for PAN-OS operations
    preval: Pre-validation checks (connectivity, licenses, HA status)
    api_client: PAN-OS XML API and REST API client implementation
    ha_manager: HA pair upgrade coordination

Subpackages:
    actions: Device operation modules (download, install, reboot, HA failover)

Example:
    Execute PAN-OS upgrade workflow::

        import os
        import json
        from swimlib.paloalto.run import main

        os.environ["SWIMLIB_DEVICE_JSON"] = json.dumps({
            "device_name": "fw-prod-01",
            "device_address": "192.168.1.100",
            "device_type_model": "PA-5220",
            "execution_type": "image_upgrade",
            "api_key": "LUFRPT14MW..."
        })

        main()

See Also:
    - :mod:`swimlib.f5` for reference implementation patterns
    - :mod:`swimlib.netscaler` for similar upgrade workflows
    - :doc:`/api/paloalto` for detailed API documentation

.. versionadded:: 0.1.0
"""

__version__ = "0.1.0"
