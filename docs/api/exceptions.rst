Exceptions Reference
====================

This section documents all custom exceptions used throughout the swimlib package.

SSH Exceptions
--------------

SSHAuthError
~~~~~~~~~~~~

.. autoexception:: swimlib.ssh_connect.SSHAuthError
   :members:
   :show-inheritance:
   :no-index:

   Raised when SSH authentication fails.

   **When Raised:**
      - Incorrect username or password
      - Authentication method mismatch
      - Paramiko AuthenticationException occurred

   **Example:**

   .. code-block:: python

      from swimlib.ssh_connect import SSHConnection, SSHAuthError

      try:
          with SSHConnection("device.example.com", "admin", "wrong_pass") as ssh:
              pass
      except SSHAuthError as e:
          logger.error(f"Failed to authenticate: {e}")
          # Handle authentication failure

RemoteStorageError
~~~~~~~~~~~~~~~~~~

.. autoexception:: swimlib.ssh_connect.RemoteStorageError
   :members:
   :show-inheritance:
   :no-index:

   Raised when remote storage validation fails.

   **When Raised:**
      - Remote folder does not exist
      - Insufficient disk space (below min_gb threshold)
      - Unable to determine disk space availability

   **Example:**

   .. code-block:: python

      from swimlib.ssh_connect import validate_remote_storage, RemoteStorageError

      try:
          validate_remote_storage(ssh_client, "/shared/images", min_gb=20)
      except RemoteStorageError as e:
          logger.error(f"Storage validation failed: {e}")
          # Handle storage issues (cleanup, use alternate location, etc.)

F5 Exceptions
-------------

SoftwareLookupException
~~~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: swimlib.f5.preval.SoftwareLookupException
   :members:
   :show-inheritance:
   :no-index:

   Raised when software configuration lookup or validation fails.

   **When Raised:**
      - Device model not found in software_matrix
      - Required image files missing from local storage
      - Image file path validation failed

   **Example:**

   .. code-block:: python

      from swimlib.f5.preval import get_target_software, SoftwareLookupException

      try:
          config = get_target_software("Unknown Device Model")
      except SoftwareLookupException as e:
          logger.error(f"Software lookup failed: {e}")
          # Handle missing software configuration

Exception Hierarchy
-------------------

swimlib uses Python's built-in exception hierarchy with custom extensions:

.. code-block:: text

   BaseException
   └── Exception
       ├── SSHAuthError
       ├── RemoteStorageError
       └── SoftwareLookupException

Best Practices
--------------

Catching Specific Exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Always catch the most specific exception type first:

.. code-block:: python

   from swimlib.ssh_connect import SSHConnection, SSHAuthError, RemoteStorageError

   try:
       with SSHConnection(ip, username, password) as ssh:
           validate_remote_storage(ssh, "/shared/images", min_gb=10)
   except SSHAuthError as e:
       # Handle authentication failure specifically
       notify_team(f"Authentication failed for {ip}: {e}")
   except RemoteStorageError as e:
       # Handle storage issues specifically
       cleanup_old_files(ip)
       retry_with_cleanup()
   except Exception as e:
       # Handle unexpected errors
       logger.exception("Unexpected error during validation")
       raise

Preserving Exception Context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``raise ... from e`` to preserve exception chains:

.. code-block:: python

   def custom_validation(ssh_client):
       try:
           validate_remote_storage(ssh_client, "/shared/images", min_gb=5)
       except RemoteStorageError as e:
           raise RuntimeError("Pre-upgrade validation failed") from e
           # Exception chain is preserved for debugging

Logging Exceptions
~~~~~~~~~~~~~~~~~~

Use appropriate logging levels for different exceptions:

.. code-block:: python

   import logging
   from swimlib.ssh_connect import SSHAuthError, RemoteStorageError

   logger = logging.getLogger(__name__)

   try:
       # ... operations ...
   except SSHAuthError as e:
       # Critical: authentication should always work in production
       logger.critical(f"Authentication failure: {e}", exc_info=True)
   except RemoteStorageError as e:
       # Warning: storage issues may be transient
       logger.warning(f"Storage validation failed: {e}")
   except Exception as e:
       # Error: unexpected failures
       logger.error(f"Unexpected error: {e}", exc_info=True)

Testing Exception Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use pytest to test exception scenarios:

.. code-block:: python

   import pytest
   from swimlib.ssh_connect import SSHConnection, SSHAuthError

   def test_ssh_auth_failure():
       with pytest.raises(SSHAuthError) as exc_info:
           with SSHConnection("192.168.1.100", "admin", "wrong_password") as ssh:
               pass

       assert "Authentication failed" in str(exc_info.value)

   def test_remote_storage_insufficient():
       with pytest.raises(RemoteStorageError, match="Insufficient disk space"):
           # ... test code ...
