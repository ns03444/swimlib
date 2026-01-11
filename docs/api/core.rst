Core Modules
============

This section documents the core swimlib modules that provide ASDB API client functionality,
logging configuration, and software configuration matrices.

ASDB API Client
---------------

.. automodule:: swimlib.asdb
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Logging Module
--------------

.. automodule:: swimlib
   :members:
   :undoc-members:
   :show-inheritance:

The :mod:`swimlib` module configures a singleton logger with Rich terminal formatting.

Module Attributes
~~~~~~~~~~~~~~~~~

.. py:data:: log
   :type: logging.Logger

   Configured logger instance with RichHandler for colored terminal output.

   :Usage:

   .. code-block:: python

      from swimlib import log

      log.info("Starting workflow")
      log.error("Failed to connect: %s", error)

Software Matrix
---------------

.. automodule:: swimlib.software_matrix
   :members:
   :undoc-members:
   :show-inheritance:

software_matrix Dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:data:: software_matrix
   :type: Dict[str, Dict[str, Any]]

   Complete mapping of F5 BIG-IP device models to software configurations.

   :Structure:

   Each device model entry contains:

   .. code-block:: python

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
                  "download_url": "https://nexus.example.com/..."
              }
          ]
      }

   :Supported Models:

   - ``BIG-IP Virtual Edition`` - VE platforms
   - ``BIG-IP vCMP Guests`` - vCMP guest instances
   - ``BIG-IP 7200`` - Hardware platform
   - ``BIG-IP i2800`` - iSeries hardware
   - ``BIG-IP i5800`` - iSeries hardware
   - ``BIG-IP i7800`` - iSeries hardware
   - ``BIG-IP i10800`` - iSeries hardware
   - ``BIG-IP i15800`` - iSeries hardware
   - ``BIG-IP 5250`` - Legacy hardware
   - ``BIG-IP rSeries Tenant A`` - rSeries tenant

   :Example:

   .. code-block:: python

      from swimlib.software_matrix import software_matrix

      config = software_matrix["BIG-IP Virtual Edition"]
      print(f"Target version: {config['target_version']}")
      for artifact in config["artifacts"]:
          print(f"  - {artifact['filename']}")
