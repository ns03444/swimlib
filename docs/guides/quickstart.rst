Quickstart
==========

Get started with swimlib in minutes. This guide covers installation, configuration, and your first workflow.

Installation
------------

**Using Poetry** (recommended)

.. code-block:: bash

   poetry add swimlib
   poetry install

**Using pip**

.. code-block:: bash

   pip install swimlib

Environment Setup
-----------------

Configure required environment variables:

.. code-block:: bash

   export ASDB_BASE_URL="https://asdb.example.com"
   export ASDB_TOKEN="your-api-token-here"
   export ASDB_MODE="remote"           # or "local" for testing
   export SWIMLIB_LOG_LEVEL="INFO"    # DEBUG, INFO, WARNING, ERROR

.. tip::

   Use a ``.env`` file with ``python-dotenv`` for development:

   .. code-block:: bash

      # .env
      ASDB_BASE_URL=https://asdb.example.com
      ASDB_TOKEN=your-token
      ASDB_MODE=local
      SWIMLIB_LOG_LEVEL=DEBUG

Basic Workflow
--------------

**1. Initialize the client**

.. code-block:: python

   from swimlib.asdb import ASDBClient, ExecutionContext, ASDBError

   # Load from environment variables
   client = ASDBClient.from_env()

**2. Create execution context**

.. code-block:: python

   ctx = ExecutionContext(
       client=client,
       device_name="f5-prod-01",
       execution_id="exec-20260111-001",
       execution_log_id="log-456",
       execution_type="production"  # or "dry_run"
   )

**3. Run your workflow**

.. code-block:: python

   try:
       ctx.start()
       ctx.log("Starting upgrade workflow")

       # Your device operations here
       # ... SSH connections, file transfers, etc ...

       ctx.complete("Upgrade completed successfully", metadata={})

   except ASDBError as e:
       print(f"Workflow failed: {e}")
       sys.exit(1)

Complete Example: F5 Upgrade
-----------------------------

Full end-to-end F5 BIG-IP upgrade workflow:

.. code-block:: python

   import sys
   from swimlib.asdb import ASDBClient, ExecutionContext, build_upgrade_metadata, ASDBError
   from swimlib.ssh_connect import SSHConnection, validate_remote_storage
   from swimlib.f5.preval import get_target_software
   from swimlib.f5.actions.image_copy import sftp_copy_artifacts
   from swimlib.f5.actions.image_stage import stage_artifacts, get_target_volume
   from swimlib.f5.actions.image_upgrade import upgrade_to_volume

   try:
       # Initialize
       client = ASDBClient.from_env()
       ctx = ExecutionContext(
           client=client,
           device_name="bigip-prod-01",
           execution_id="exec-001",
           execution_log_id="log-001",
           execution_type="production"
       )

       ctx.start()

       # Pre-validation
       ctx.log("Validating software configuration")
       config = get_target_software("BIG-IP Virtual Edition")

       # SSH and storage checks
       ctx.log("Connecting to device")
       with SSHConnection("192.168.1.100", "admin", "password") as ssh:
           validate_remote_storage(ssh, "/shared/images", min_gb=10)

           # Image copy
           ctx.log("Transferring software images")
           sftp_copy_artifacts(ssh, config["artifacts"], "/shared/images")

           # Image stage
           ctx.log("Installing to inactive volume")
           stage_artifacts(ssh, config["artifacts"], config["target_version"])

           # Image upgrade
           ctx.log("Initiating reboot to upgraded volume")
           target_vol = get_target_volume(ssh)
           upgrade_to_volume(ssh, target_vol)

       # Complete
       metadata = build_upgrade_metadata(
           target_version=config["target_version"],
           local_folder=config["local_folder"],
           remote_folder="/shared/images"
       )
       ctx.complete("Upgrade completed successfully", metadata)

   except ASDBError as e:
       ctx.log(f"Upgrade failed: {e}", level="error")
       sys.exit(1)

Execution Types
---------------

Control workflow behavior with ``execution_type``:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Type
     - Behavior
   * - ``dry_run``
     - Validates only, no changes. Skips history creation
   * - ``production``
     - Full execution with ASDB history records

Operation Modes
---------------

Control API interaction with ``ASDB_MODE``:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Mode
     - Behavior
   * - ``remote``
     - Makes actual API calls to ASDB (production)
   * - ``local``
     - Logs operations without HTTP requests (testing)

Testing Your Setup
------------------

Verify your configuration with a simple test:

.. code-block:: python

   from swimlib.asdb import ASDBClient

   # This will validate environment variables
   try:
       client = ASDBClient.from_env()
       print("✅ Configuration valid")
       print(f"   Base URL: {client.base_url}")
       print(f"   Mode: {client.mode}")
   except Exception as e:
       print(f"❌ Configuration error: {e}")

Next Steps
----------

* :doc:`configuration` - Detailed configuration options
* :doc:`../api/f5` - F5 BIG-IP module documentation
* :doc:`../examples/f5_upgrade` - Complete F5 upgrade examples
* :doc:`../development/contributing` - Contributing guidelines

.. seealso::

   **Quick Reference**

   - :class:`swimlib.asdb.ASDBClient` - Low-level ASDB client
   - :class:`swimlib.asdb.ExecutionContext` - High-level orchestrator
   - :class:`swimlib.ssh_connect.SSHConnection` - SSH context manager
