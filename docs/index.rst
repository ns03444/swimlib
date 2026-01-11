swimlib
=======

.. image:: https://img.shields.io/badge/python-3.13+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

Production-grade Python SDK for automating network device upgrades via ASDB API.

**Fast, reliable, built for production** – Manage F5 BIG-IP, NetScaler, and Palo Alto upgrades with intelligent automation and comprehensive tracking.

----

Quick Start
-----------

Install with Poetry:

.. code-block:: bash

   poetry add swimlib

Basic usage:

.. code-block:: python

   from swimlib.asdb import ASDBClient, ExecutionContext

   # Initialize from environment
   client = ASDBClient.from_env()

   ctx = ExecutionContext(
       client=client,
       device_name="f5-prod-01",
       execution_id="exec-123",
       execution_log_id="log-456",
       execution_type="production"
   )

   ctx.start()
   ctx.log("Starting upgrade...")
   # ... do work ...
   ctx.complete("Success", metadata)

Set environment variables:

.. code-block:: bash

   export ASDB_BASE_URL="https://asdb.example.com"
   export ASDB_TOKEN="your-token"
   export ASDB_MODE="remote"

----

Documentation
-------------

.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   guides/quickstart
   guides/configuration

.. toctree::
   :maxdepth: 2
   :caption: Platform Modules

   api/f5
   api/netscaler
   api/paloalto

.. toctree::
   :maxdepth: 1
   :caption: Core API

   api/core
   api/ssh
   api/exceptions

.. toctree::
   :maxdepth: 1
   :caption: Resources

   examples/f5_upgrade
   development/contributing

----

Platform Support
----------------

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Platform
     - Status
     - Target Versions
   * - **F5 BIG-IP**
     - ✅ Production
     - VE/vCMP: 21.0.0 | iSeries: 17.5.1.3
   * - **NetScaler**
     - 🚧 Development
     - Coming soon
   * - **Palo Alto**
     - 🚧 Development
     - Coming soon

----

Architecture
------------

.. code-block:: text

   CLI App
      │
      ├─► ExecutionContext ──► ASDBClient ──► ASDB API
      │                             │
      │                             ├─► Logging
      │                             ├─► Status tracking
      │                             └─► History records
      │
      └─► SSHConnection ──────────────────► Network Device
                                              │
                                              ├─► SFTP transfer
                                              ├─► Command execution
                                              └─► Validation

**Design Principles**

Exception-based
   Raises ``ASDBError`` instead of ``sys.exit()`` – your app decides how to handle failures

Graceful degradation
   ASDB API failures logged but don't break execution

Mode switching
   ``remote`` for production | ``local`` for testing

Execution types
   ``production`` persists history | ``dry_run`` validates only

----

F5 Workflow Phases
------------------

1. **dry_run** – Pre-validation (SSH, storage, software lookup)
2. **image_copy** – SFTP transfer with MD5 validation
3. **image_stage** – Install to inactive volume (no reboot)
4. **image_upgrade** – Reboot to upgraded volume

----

Links
-----

* 📦 PyPI: https://pypi.org/project/swimlib
* 🐛 Issues: https://github.com/nickspell/swimlib/issues
* 📚 Source: https://github.com/nickspell/swimlib

----

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
