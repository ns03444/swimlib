"""Software Upgrade: Pre-Checks"""

import os
import logging
from swimlib.software_matrix import software_matrix

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class SoftwareLookupException(Exception):
    """Custom exception for software lookup and validation failures."""
    pass


# Based on device model, determine target softwre version and validate filepath/file exists.

def get_target_software(device_model):
    """
    Validate local software images exist for the given device model.

    Args:
        device_model: F5 BIG-IP platform name (e.g., "BIG-IP Virtual Edition")

    Returns:
        dict: Software configuration with validated artifact paths

    Raises:
        SoftwareLookupException: If device model not found in matrix or image files missing
    """
    if device_model not in software_matrix:
        raise SoftwareLookupException(f"Device model '{device_model}' not found in software matrix")

    config = software_matrix[device_model]

    for artifact in config["artifacts"]:
        if not os.path.exists(artifact["local_path"]):
            raise SoftwareLookupException(f"Missing required image: {artifact['local_path']}")

    return config
 