"""
software_matrix.py

A complete and consistent configuration matrix for F5 BIG-IP software images across various platforms.
This version has been expanded with additional common platforms based on F5's iSeries and legacy hardware lines.
The target versions have been updated to reflect current supported releases as of late 2025:
- Virtual Edition and vCMP Guests: 21.0.0 (latest major release)
- Hardware platforms (iSeries, etc.): 17.5.1.3-0.125.19 (long-term supported engineering hotfix branch)

Artifacts include typical image types:
- .iso for base installations (VE, vCMP)
- .ALL-FSOS.qcow2.zip for virtualized hardware deployments
- Hotfix .iso for engineering hotfixes

All MD5 values are realistic 32-character mock hex strings.
Download URLs follow the observed internal Nexus repository pattern.
Paths are consistent per version.
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