Quick Start Guide
=================

Get up and running with swimlib in minutes. This guide walks through basic usage
patterns and common workflows.

Basic ASDB Client Usage
-----------------------

Initialize and use the ASDB client:

.. code-block:: python

   from swimlib.asdb import ASDBClient
   from swimlib import log

   # Initialize client with environment variables
   client = ASDBClient(
       device={
           "execution_log_id": "log-123",
           "device_name": "router-01",
           "execution_type": "production"
       }
   )

   # Send log entries
   client.send_log("Starting device validation", log_level="info")
   log.info("Validation workflow initiated")

   # Update execution status
   client.update_execution_log_status("log-123", "inprogress")

SSH Connection Example
----------------------

Connect to F5 device and execute commands:

.. code-block:: python

   from swimlib.ssh_connect import SSHConnection, validate_remote_storage

   with SSHConnection("192.168.1.100", "admin", "password") as ssh:
       # Execute command
       stdin, stdout, stderr = ssh.exec_command("tmsh show sys version")
       version = stdout.read().decode()
       print(f"Device version: {version}")

       # Validate storage
       validate_remote_storage(ssh, "/shared/images", min_gb=10)
       print("✓ Storage validation passed")

Complete F5 Upgrade Workflow
-----------------------------

Pre-validation dry run:

.. code-block:: python

   import os
   import json
   from swimlib.asdb import ASDBClient
   from swimlib.ssh_connect import SSHConnection, validate_remote_storage
   from swimlib.f5.preval import get_target_software

   # Configure device
   device = {
       "device_name": "bigip-01.example.com",
       "device_address": "192.168.1.100",
       "device_type_model": "BIG-IP Virtual Edition",
       "execution_id": "exec-789",
       "execution_log_id": "log-456",
       "execution_type": "dry_run"  # Pre-validation only
   }

   # Initialize ASDB client
   client = ASDBClient(device=device)

   # Phase 1: Software validation
   config = get_target_software(device["device_type_model"])
   client.send_log(f"Target version: {config['target_version']}")

   # Phase 2: SSH connectivity
   with SSHConnection(
       device["device_address"],
       os.getenv("SWIMLIB_SSH_USERNAME", "admin"),
       os.getenv("SWIMLIB_SSH_PASSWORD", "admin")
   ) as ssh:
       client.send_log("SSH connection established")

       # Phase 3: Storage validation
       validate_remote_storage(ssh, "/shared/images", min_gb=10)
       client.send_log("Storage validation passed")

   # Complete dry run
   client.pass_device_execution("Pre-validation successful")

Environment Configuration
-------------------------

Create a ``.env`` file:

.. code-block:: bash

   # ASDB Configuration
   ASDB_BASE_URL=https://asdb.example.com
   ASDB_TOKEN=your-api-token-here
   ASDB_MODE=remote  # or 'local' for testing

   # Logging Configuration
   SWIMLIB_LOG_LEVEL=INFO

   # SSH Credentials
   SWIMLIB_SSH_USERNAME=admin
   SWIMLIB_SSH_PASSWORD=your-password-here

Load environment variables:

.. code-block:: python

   import os
   from dotenv import load_dotenv

   load_dotenv()  # Load .env file

   # Now environment variables are available
   assert os.getenv("ASDB_BASE_URL") is not None

Local Mode Testing
------------------

Test workflows without making real API calls:

.. code-block:: python

   from swimlib.asdb import ASDBClient

   # Initialize in local mode
   client = ASDBClient(
       base_url="https://asdb.example.com",
       api_token="dummy-token",
       mode="local",  # Logs requests without HTTP calls
       device={"execution_log_id": "test-123"}
   )

   # These operations are logged but don't make HTTP requests
   client.update_execution_log_status("test-123", "inprogress")
   client.send_log("Testing local mode")

   # Output:
   # [ASDB local] PATCH https://asdb.example.com/swimv2/execution_log/test-123/ ...
   # [ASDB local] POST https://asdb.example.com/swimv2/execution_log/test-123/append_log/ ...

Next Steps
----------

- :doc:`configuration` - Detailed environment configuration
- :doc:`workflows` - Advanced workflow patterns
- :doc:`testing` - Testing strategies
- :doc:`../examples/f5_upgrade` - Complete F5 upgrade example
