Configuration Guide
===================

Comprehensive guide to configuring swimlib for different environments.

Environment Variables
---------------------

Required Variables
~~~~~~~~~~~~~~~~~~

ASDB_BASE_URL
^^^^^^^^^^^^^

Base URL for the ASDB API endpoint.

.. code-block:: bash

   export ASDB_BASE_URL="https://asdb.example.com"

**Usage:** Used by ASDBClient to construct API endpoint URLs.

ASDB_TOKEN
^^^^^^^^^^

API authentication token for ASDB.

.. code-block:: bash

   export ASDB_TOKEN="your-api-token-here"

**Security:** Store in secure credential management systems. Never commit to version control.

Optional Variables
~~~~~~~~~~~~~~~~~~

ASDB_MODE
^^^^^^^^^

Operation mode for ASDB client.

.. code-block:: bash

   export ASDB_MODE="remote"  # or "local"

**Values:**
   - ``remote`` (default): Makes actual HTTP API calls
   - ``local``: Logs operations without network requests (testing/dry-run)

SWIMLIB_LOG_LEVEL
^^^^^^^^^^^^^^^^^

Logging verbosity level.

.. code-block:: bash

   export SWIMLIB_LOG_LEVEL="INFO"

**Values:** DEBUG, INFO, WARNING, ERROR

SWIMLIB_SSH_USERNAME
^^^^^^^^^^^^^^^^^^^^

Default SSH username for device connections.

.. code-block:: bash

   export SWIMLIB_SSH_USERNAME="admin"

**Default:** "admin"

SWIMLIB_SSH_PASSWORD
^^^^^^^^^^^^^^^^^^^^

Default SSH password for device connections.

.. code-block:: bash

   export SWIMLIB_SSH_PASSWORD="your-password-here"

**Security:** Use secure credential management. Consider SSH key-based auth for production.

**Default:** "admin"

SWIMLIB_DEVICE_JSON
^^^^^^^^^^^^^^^^^^^

Device configuration as JSON string (used by F5 runner).

.. code-block:: bash

   export SWIMLIB_DEVICE_JSON='{
       "device_name": "bigip-01",
       "device_address": "192.168.1.100",
       "device_type_model": "BIG-IP Virtual Edition",
       "execution_id": "exec-123",
       "execution_log_id": "log-456",
       "execution_type": "dry_run"
   }'

Configuration Patterns
----------------------

Using .env Files
~~~~~~~~~~~~~~~~

Create ``.env`` file in project root:

.. code-block:: bash

   # .env
   ASDB_BASE_URL=https://asdb.example.com
   ASDB_TOKEN=token_abc123
   ASDB_MODE=remote
   SWIMLIB_LOG_LEVEL=DEBUG
   SWIMLIB_SSH_USERNAME=admin
   SWIMLIB_SSH_PASSWORD=secure_password

Load with python-dotenv:

.. code-block:: python

   from dotenv import load_dotenv
   load_dotenv()  # Loads .env file into os.environ

Using Configuration Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create configuration dataclass:

.. code-block:: python

   from dataclasses import dataclass
   import os

   @dataclass
   class SwimLibConfig:
       asdb_url: str
       asdb_token: str
       mode: str = "remote"
       log_level: str = "INFO"

       @classmethod
       def from_env(cls):
           return cls(
               asdb_url=os.getenv("ASDB_BASE_URL"),
               asdb_token=os.getenv("ASDB_TOKEN"),
               mode=os.getenv("ASDB_MODE", "remote"),
               log_level=os.getenv("SWIMLIB_LOG_LEVEL", "INFO")
           )

   # Usage
   config = SwimLibConfig.from_env()
   client = ASDBClient(
       base_url=config.asdb_url,
       api_token=config.asdb_token,
       mode=config.mode
   )

Environment-Specific Configurations
------------------------------------

Development Environment
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # .env.development
   ASDB_BASE_URL=https://asdb-dev.example.com
   ASDB_TOKEN=dev_token_123
   ASDB_MODE=local  # Don't make real API calls
   SWIMLIB_LOG_LEVEL=DEBUG

Staging Environment
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # .env.staging
   ASDB_BASE_URL=https://asdb-staging.example.com
   ASDB_TOKEN=staging_token_456
   ASDB_MODE=remote
   SWIMLIB_LOG_LEVEL=INFO

Production Environment
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # .env.production
   ASDB_BASE_URL=https://asdb.example.com
   ASDB_TOKEN=${VAULT_ASDB_TOKEN}  # From secret manager
   ASDB_MODE=remote
   SWIMLIB_LOG_LEVEL=WARNING

Credential Management
---------------------

Best Practices
~~~~~~~~~~~~~~

1. **Never commit credentials to version control**

   Add to ``.gitignore``:

   .. code-block:: text

      .env
      .env.*
      *.pem
      *.key

2. **Use secret management systems**

   - HashiCorp Vault
   - AWS Secrets Manager
   - Azure Key Vault
   - Environment-specific CI/CD secrets

3. **Rotate credentials regularly**

4. **Use least-privilege access**

Example with HashiCorp Vault
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import hvac
   import os

   # Initialize Vault client
   vault_client = hvac.Client(
       url=os.getenv("VAULT_ADDR"),
       token=os.getenv("VAULT_TOKEN")
   )

   # Read secrets
   secrets = vault_client.secrets.kv.v2.read_secret_version(
       path="swimlib/production"
   )

   # Configure ASDBClient with vault secrets
   client = ASDBClient(
       base_url=secrets["data"]["data"]["asdb_url"],
       api_token=secrets["data"]["data"]["asdb_token"],
       mode="remote"
   )

Validation
----------

Validate configuration at startup:

.. code-block:: python

   import os
   import sys
   from swimlib import log

   def validate_config():
       """Validate required environment variables."""
       required = {
           "ASDB_BASE_URL": os.getenv("ASDB_BASE_URL"),
           "ASDB_TOKEN": os.getenv("ASDB_TOKEN"),
       }

       missing = [k for k, v in required.items() if not v]

       if missing:
           log.error(f"Missing required environment variables: {', '.join(missing)}")
           sys.exit(1)

       log.info("✓ Configuration validated")

   # Call at application startup
   validate_config()

Next Steps
----------

- :doc:`workflows` - Common workflow patterns
- :doc:`testing` - Testing with different configurations
- :doc:`best_practices` - Security and operational best practices
