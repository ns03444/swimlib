SSH Connection Management
=========================

This section documents the SSH connection management module for F5 BIG-IP devices,
including context managers and remote storage validation.

Module Overview
---------------

.. automodule:: swimlib.ssh_connect
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions
----------

SSHAuthError
~~~~~~~~~~~~

.. autoexception:: swimlib.ssh_connect.SSHAuthError
   :members:
   :show-inheritance:
   :no-index:

   Raised when SSH authentication fails during connection establishment.

   :Example:

   .. code-block:: python

      from swimlib.ssh_connect import SSHConnection, SSHAuthError

      try:
          with SSHConnection("192.168.1.100", "admin", "wrong_password") as ssh:
              ssh.exec_command("ls")
      except SSHAuthError as e:
          print(f"Authentication failed: {e}")

RemoteStorageError
~~~~~~~~~~~~~~~~~~

.. autoexception:: swimlib.ssh_connect.RemoteStorageError
   :members:
   :show-inheritance:
   :no-index:

   Raised when remote storage validation fails (folder missing or insufficient disk space).

   :Example:

   .. code-block:: python

      from swimlib.ssh_connect import validate_remote_storage, RemoteStorageError

      try:
          validate_remote_storage(ssh_client, "/shared/images", min_gb=20)
      except RemoteStorageError as e:
          print(f"Storage validation failed: {e}")

Classes
-------

SSHConnection
~~~~~~~~~~~~~

.. autoclass:: swimlib.ssh_connect.SSHConnection
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __enter__, __exit__
   :no-index:

   Context manager for paramiko SSH connections with automatic cleanup.

   :Usage Example:

   .. code-block:: python

      from swimlib.ssh_connect import SSHConnection

      with SSHConnection("192.168.1.100", "admin", "password") as ssh:
          stdin, stdout, stderr = ssh.exec_command("tmsh show sys version")
          version = stdout.read().decode()
          print(f"Device version: {version}")

   :Attributes:

   .. py:attribute:: ip
      :type: str

      IP address or hostname of the remote device.

   .. py:attribute:: username
      :type: str

      SSH username for authentication.

   .. py:attribute:: password
      :type: str

      SSH password for authentication.

   .. py:attribute:: client
      :type: paramiko.SSHClient | None

      The underlying paramiko SSH client instance.

Functions
---------

validate_remote_storage
~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: swimlib.ssh_connect.validate_remote_storage
   :no-index:

   Validates that a remote folder exists and has sufficient disk space.

   :Usage Example:

   .. code-block:: python

      from swimlib.ssh_connect import SSHConnection, validate_remote_storage

      with SSHConnection("192.168.1.100", "admin", "password") as ssh:
          # Ensure 20GB free on /shared/images
          validate_remote_storage(ssh, "/shared/images", min_gb=20)
          print("✓ Storage validation passed")

   :Validation Steps:

   1. Checks if the specified folder exists using ``test -d``
   2. Extracts the mount point from the folder path
   3. Queries available disk space using ``df -BG``
   4. Compares available space against minimum requirement
   5. Raises RemoteStorageError if validation fails
