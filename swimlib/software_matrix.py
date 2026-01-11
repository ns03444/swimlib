"""F5 BIG-IP Software Configuration Matrix.

This module provides a comprehensive configuration matrix mapping F5 BIG-IP device models
to their corresponding software images, versions, storage paths, and download locations.

The matrix supports multiple platform types including:
- Virtual Edition (VE) platforms
- vCMP Guest platforms
- Hardware iSeries platforms (i2800, i5800, i7800, i10800, i15800)
- Legacy hardware platforms (5250, 7200)
- rSeries tenant platforms

Each device model configuration includes:
- Target software version
- Local and remote storage folder paths
- Software artifact details (filenames, paths, MD5 checksums, download URLs)

Module Attributes:
    software_matrix (Dict[str, Dict[str, Any]]): Complete mapping of device models to
        software configurations. Keys are device model names (e.g., "BIG-IP Virtual Edition"),
        values are configuration dictionaries.

Software Version Strategy:
    - Virtual Edition and vCMP Guests: 21.0.0 (latest major release)
    - Hardware platforms (iSeries): 17.5.1.3-0.125.19 (long-term supported EHF branch)
    - rSeries platforms: 21.0.0

Artifact Types:
    - ``.iso`` - Base installation images for VE and vCMP platforms
    - ``.ALL-FSOS.qcow2.zip`` - Virtualized hardware deployment images
    - ``Hotfix-*.iso`` - Engineering hotfix (EHF) images

Example:
    Look up software configuration for a device model::

        from swimlib.software_matrix import software_matrix

        config = software_matrix["BIG-IP Virtual Edition"]
        print(f"Target version: {config['target_version']}")
        print(f"Artifacts: {len(config['artifacts'])}")

        for artifact in config["artifacts"]:
            print(f"  - {artifact['filename']} (MD5: {artifact['md5']})")

    Validate artifact existence::

        import os
        from swimlib.software_matrix import software_matrix

        config = software_matrix["BIG-IP i7800"]
        for artifact in config["artifacts"]:
            if os.path.exists(artifact["local_path"]):
                print(f"✓ {artifact['filename']}")
            else:
                print(f"✗ {artifact['filename']} NOT FOUND")

Configuration Structure:
    Each device model entry contains::

        {
            "target_version": "21.0.0",
            "local_folder": "/project-volume/images/21.0.0/",
            "remote_folder": "/shared/images/",
            "artifacts": [
                {
                    "filename": "BIGIP-21.0.0.iso",
                    "local_path": "/project-volume/images/21.0.0/BIGIP-21.0.0.iso",
                    "remote_path": "/shared/images/BIGIP-21.0.0.iso",
                    "md5": "a1b2c3d4e5f678901234567890123456",
                    "download_url": "https://nexus-dev.onef5serv.net/repository/..."
                }
            ]
        }

Note:
    MD5 checksums in this matrix are mock values for demonstration purposes. In production,
    these should be replaced with actual checksums from F5 Networks or verified downloads.

    Download URLs point to an internal Nexus repository pattern and should be updated
    to match your organization's artifact repository.

See Also:
    - :func:`swimlib.f5.preval.get_target_software` for retrieving and validating configurations
    - :func:`swimlib.f5.actions.image_copy.sftp_copy_artifacts` for artifact transfer operations

.. versionadded:: 0.1.0
"""

software_matrix = {
    "BIG-IP vCMP Guests": {
        "target_version": "21.0.0",
        "local_folder": "/project-volume/images/21.0.0/",
        "remote_folder": "/shared/images/",
        "artifacts": [
            {
                "filename": "BIGIP-21.0.0.iso",
                "local_path": "/project-volume/images/21.0.0/BIGIP-21.0.0.iso",
                "remote_path": "/shared/images/BIGIP-21.0.0.iso",
                "md5": "a1b2c3d4e5f678901234567890123456",
                "download_url": "https://nexus-dev.onef5serv.net/repository/network-device-images/f5/21.0.0/BIGIP-21.0.0.iso"
            }
        ]
    },
    "BIG-IP Virtual Edition": {
        "target_version": "21.0.0",
        "local_folder": "/project-volume/images/21.0.0/",
        "remote_folder": "/shared/images/",
        "artifacts": [
            {
                "filename": "BIGIP-21.0.0.iso",
                "local_path": "/project-volume/images/21.0.0/BIGIP-21.0.0.iso",
                "remote_path": "/shared/images/BIGIP-21.0.0.iso",
                "md5": "f6e7d8c9b0a1234567890123456789ab",
                "download_url": "https://nexus-dev.onef5serv.net/repository/network-device-images/f5/21.0.0/BIGIP-21.0.0.iso"
            },
            {
                "filename": "BIGIP-21.0.0.ALL-FSOS.qcow2.zip",
                "local_path": "/project-volume/images/21.0.0/BIGIP-21.0.0.ALL-FSOS.qcow2.zip",
                "remote_path": "/shared/images/BIGIP-21.0.0.ALL-FSOS.qcow2.zip",
                "md5": "1234567890abcdef1234567890abcdef",
                "download_url": "https://nexus-dev.onef5serv.net/repository/network-device-images/f5/21.0.0/BIGIP-21.0.0.ALL-FSOS.qcow2.zip"
            }
        ]
    },
    "BIG-IP 7200": {
        "target_version": "17.5.1.3-0.125.19",
        "local_folder": "/project-volume/images/17.5.1.3-0.125.19/",
        "remote_folder": "/shared/images/",
        "artifacts": [
            {
                "filename": "BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip",
                "local_path": "/project-volume/images/17.5.1.3-0.125.19/BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip",
                "remote_path": "/shared/images/BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip",
                "md5": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7",
                "download_url": "https://nexus-dev.onef5serv.net/repository/network-device-images/f5/17.5.1.3-0.125.19/BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip"
            },
            {
                "filename": "Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso",
                "local_path": "/project-volume/images/17.5.1.3-0.125.19/Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso",
                "remote_path": "/shared/images/Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso",
                "md5": "c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8",
                "download_url": "https://nexus-dev.onef5serv.net/repository/network-device-images/f5/17.5.1.3-0.125.19/Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso"
            }
        ]
    },
    "BIG-IP i2800": {
        "target_version": "17.5.1.3-0.125.19",
        "local_folder": "/project-volume/images/17.5.1.3-0.125.19/",
        "remote_folder": "/shared/images/",
        "artifacts": [
            {
                "filename": "BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip",
                "local_path": "/project-volume/images/17.5.1.3-0.125.19/BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip",
                "remote_path": "/shared/images/BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip",
                "md5": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7",
                "download_url": "https://nexus-dev.onef5serv.net/repository/network-device-images/f5/17.5.1.3-0.125.19/BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip"
            },
            {
                "filename": "Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso",
                "local_path": "/project-volume/images/17.5.1.3-0.125.19/Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso",
                "remote_path": "/shared/images/Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso",
                "md5": "c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8",
                "download_url": "https://nexus-dev.onef5serv.net/repository/network-device-images/f5/17.5.1.3-0.125.19/Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso"
            }
        ]
    },
    "BIG-IP i5800": {
        "target_version": "17.5.1.3-0.125.19",
        "local_folder": "/project-volume/images/17.5.1.3-0.125.19/",
        "remote_folder": "/shared/images/",
        "artifacts": [
            {
                "filename": "BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip",
                "local_path": "/project-volume/images/17.5.1.3-0.125.19/BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip",
                "remote_path": "/shared/images/BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip",
                "md5": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7",
                "download_url": "https://nexus-dev.onef5serv.net/repository/network-device-images/f5/17.5.1.3-0.125.19/BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip"
            },
            {
                "filename": "Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso",
                "local_path": "/project-volume/images/17.5.1.3-0.125.19/Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso",
                "remote_path": "/shared/images/Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso",
                "md5": "c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8",
                "download_url": "https://nexus-dev.onef5serv.net/repository/network-device-images/f5/17.5.1.3-0.125.19/Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso"
            }
        ]
    },
    "BIG-IP i7800": {
        "target_version": "17.5.1.3-0.125.19",
        "local_folder": "/project-volume/images/17.5.1.3-0.125.19/",
        "remote_folder": "/shared/images/",
        "artifacts": [
            {
                "filename": "BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip",
                "local_path": "/project-volume/images/17.5.1.3-0.125.19/BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip",
                "remote_path": "/shared/images/BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip",
                "md5": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7",
                "download_url": "https://nexus-dev.onef5serv.net/repository/network-device-images/f5/17.5.1.3-0.125.19/BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip"
            },
            {
                "filename": "Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso",
                "local_path": "/project-volume/images/17.5.1.3-0.125.19/Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso",
                "remote_path": "/shared/images/Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso",
                "md5": "c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8",
                "download_url": "https://nexus-dev.onef5serv.net/repository/network-device-images/f5/17.5.1.3-0.125.19/Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso"
            }
        ]
    },
    "BIG-IP i10800": {
        "target_version": "17.5.1.3-0.125.19",
        "local_folder": "/project-volume/images/17.5.1.3-0.125.19/",
        "remote_folder": "/shared/images/",
        "artifacts": [
            {
                "filename": "BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip",
                "local_path": "/project-volume/images/17.5.1.3-0.125.19/BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip",
                "remote_path": "/shared/images/BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip",
                "md5": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7",
                "download_url": "https://nexus-dev.onef5serv.net/repository/network-device-images/f5/17.5.1.3-0.125.19/BIGIP-17.5.1.3-0.125.19.ALL-FSOS.qcow2.zip"
            },
            {
                "filename": "Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso",
                "local_path": "/project-volume/images/17.5.1.3-0.125.19/Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso",
                "remote_path": "/shared/images/Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso",
                "md5": "c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8",
                "download_url": "https://nexus-dev.onef5serv.net/repository/network-device-images/f5/17.5.1.3-0.125.19/Hotfix-BIGIP-17.5.1.3-0.125.19-ENG.iso"
            }
        ]
    },

    # Added sample models with mock data
    "BIG-IP i15800": {
        "target_version": "17.5.1.3-0.125.19",
        "local_folder": "/project-volume/images/17.5.1.3-0.125.19/",
        "remote_folder": "/shared/images/",
        "artifacts": [
            {
                "filename": "BIGIP-17.5.1.3-0.125.19.i15800.ALL-FSOS.qcow2.zip",
                "local_path": "/project-volume/images/17.5.1.3-0.125.19/BIGIP-17.5.1.3-0.125.19.i15800.ALL-FSOS.qcow2.zip",
                "remote_path": "/shared/images/BIGIP-17.5.1.3-0.125.19.i15800.ALL-FSOS.qcow2.zip",
                "md5": "d4e5f6a7b8c9d0e1f2a3b4c5d6e7f809",
                "download_url": "https://nexus-dev.onef5serv.net/repository/network-device-images/f5/17.5.1.3-0.125.19/BIGIP-17.5.1.3-0.125.19.i15800.ALL-FSOS.qcow2.zip"
            }
        ]
    },
    "BIG-IP 5250": {
        "target_version": "17.5.1.3-0.125.19",
        "local_folder": "/project-volume/images/17.5.1.3-0.125.19/",
        "remote_folder": "/shared/images/",
        "artifacts": [
            {
                "filename": "BIGIP-17.5.1.3-0.125.19.5250.ALL-FSOS.qcow2.zip",
                "local_path": "/project-volume/images/17.5.1.3-0.125.19/BIGIP-17.5.1.3-0.125.19.5250.ALL-FSOS.qcow2.zip",
                "remote_path": "/shared/images/BIGIP-17.5.1.3-0.125.19.5250.ALL-FSOS.qcow2.zip",
                "md5": "e5f6a7b8c9d0e1f2a3b4c5d6e7f8091a",
                "download_url": "https://nexus-dev.onef5serv.net/repository/network-device-images/f5/17.5.1.3-0.125.19/BIGIP-17.5.1.3-0.125.19.5250.ALL-FSOS.qcow2.zip"
            },
            {
                "filename": "Hotfix-BIGIP-17.5.1.3-0.125.19-5250-ENG.iso",
                "local_path": "/project-volume/images/17.5.1.3-0.125.19/Hotfix-BIGIP-17.5.1.3-0.125.19-5250-ENG.iso",
                "remote_path": "/shared/images/Hotfix-BIGIP-17.5.1.3-0.125.19-5250-ENG.iso",
                "md5": "f6a7b8c9d0e1f2a3b4c5d6e7f8091a2b",
                "download_url": "https://nexus-dev.onef5serv.net/repository/network-device-images/f5/17.5.1.3-0.125.19/Hotfix-BIGIP-17.5.1.3-0.125.19-5250-ENG.iso"
            }
        ]
    },
    "BIG-IP rSeries Tenant A": {
        "target_version": "21.0.0",
        "local_folder": "/project-volume/images/rseries/21.0.0/",
        "remote_folder": "/shared/images/rseries/",
        "artifacts": [
            {
                "filename": "BIGIP-rseries-tenantA-21.0.0.iso",
                "local_path": "/project-volume/images/rseries/21.0.0/BIGIP-rseries-tenantA-21.0.0.iso",
                "remote_path": "/shared/images/rseries/BIGIP-rseries-tenantA-21.0.0.iso",
                "md5": "9a8b7c6d5e4f301234567890abcdef12",
                "download_url": "https://nexus-dev.onef5serv.net/repository/network-device-images/f5/rseries/21.0.0/BIGIP-rseries-tenantA-21.0.0.iso"
            }
        ]
    }
    # Additional platforms (e.g., i15800, rSeries tenants, older 5000/7000 series) can be added following the same pattern.
}