"""SSH Connection Manager for F5 BIG-IP Devices.

This module provides SSH connection management functionality with context manager support
for secure, automated connections to F5 BIG-IP devices. It includes utilities for remote
storage validation and connection error handling.

The module uses Paramiko for SSH/SFTP operations and implements custom exception types
for specific failure scenarios.

Classes:
    SSHConnection: Context manager for paramiko SSH connections with automatic cleanup.
    SSHAuthError: Exception raised when SSH authentication fails.
    RemoteStorageError: Exception raised when remote storage validation fails.

Functions:
    validate_remote_storage: Validates remote folder existence and available disk space.

Example:
    Basic SSH connection with context manager::

        from swimlib.ssh_connect import SSHConnection

        with SSHConnection("192.168.1.100", "admin", "password") as ssh:
            stdin, stdout, stderr = ssh.exec_command("tmsh show sys version")
            version = stdout.read().decode()
            print(f"Device version: {version}")

    Validate remote storage before file transfer::

        from swimlib.ssh_connect import SSHConnection, validate_remote_storage

        with SSHConnection("192.168.1.100", "admin", "password") as ssh:
            validate_remote_storage(ssh, "/shared/images", min_gb=10)
            # Proceed with file transfer if validation passes

Note:
    This module disables key-based authentication and requires password authentication.
    Host key checking is disabled (AutoAddPolicy), which should be reconsidered for
    production security requirements.

See Also:
    - :mod:`paramiko` for underlying SSH functionality
    - :mod:`swimlib.f5.actions.image_copy` for SFTP file transfer implementation

.. versionadded:: 0.1.0
"""

from paramiko import SSHClient, AutoAddPolicy, AuthenticationException


class SSHAuthError(Exception):
    """Custom exception raised when SSH authentication fails.

    This exception is raised when paramiko.AuthenticationException occurs during
    SSH connection establishment, typically due to incorrect credentials or
    authentication method mismatches.

    Example:
        Handle SSH authentication errors::

            from swimlib.ssh_connect import SSHConnection, SSHAuthError

            try:
                with SSHConnection("192.168.1.100", "admin", "wrong_pass") as ssh:
                    pass
            except SSHAuthError as e:
                print(f"Authentication failed: {e}")

    .. versionadded:: 0.1.0
    """
    pass


class RemoteStorageError(Exception):
    """Custom exception raised when remote storage validation fails.

    This exception is raised by validate_remote_storage() when:
    - The specified remote folder does not exist
    - Insufficient disk space is available on the remote system
    - Unable to determine disk space availability

    Example:
        Handle storage validation errors::

            from swimlib.ssh_connect import RemoteStorageError, validate_remote_storage

            try:
                validate_remote_storage(ssh_client, "/shared/images", min_gb=20)
            except RemoteStorageError as e:
                print(f"Storage validation failed: {e}")

    .. versionadded:: 0.1.0
    """
    pass


class SSHConnection:
    """Context manager for paramiko SSH connections with automatic resource cleanup.

    This class provides a convenient context manager interface for establishing SSH
    connections to F5 BIG-IP devices. It automatically handles connection cleanup on
    exit and raises custom exceptions for authentication failures.

    The connection disables key-based authentication and requires password authentication.
    Host key verification is disabled via AutoAddPolicy.

    Attributes:
        ip (str): IP address or hostname of the remote device.
        username (str): SSH username for authentication.
        password (str): SSH password for authentication.
        client (paramiko.SSHClient | None): The underlying paramiko SSH client instance.

    Example:
        Execute remote commands with automatic cleanup::

            with SSHConnection("192.168.1.100", "admin", "password") as ssh:
                stdin, stdout, stderr = ssh.exec_command("tmsh show sys version")
                output = stdout.read().decode()

        Handle connection errors::

            try:
                with SSHConnection("192.168.1.100", "admin", "wrong_pass") as ssh:
                    ssh.exec_command("ls /shared/images")
            except SSHAuthError as e:
                print(f"Failed to authenticate: {e}")

    Warning:
        This implementation disables host key verification (AutoAddPolicy) and
        key-based authentication. For production environments, consider implementing
        proper host key verification and supporting key-based authentication.

    .. versionadded:: 0.1.0
    """

    def __init__(self, ip, username, password):
        """Initialize SSH connection context manager.

        :param ip: IP address or hostname of the remote device
        :type ip: str
        :param username: SSH username for authentication
        :type username: str
        :param password: SSH password for authentication
        :type password: str

        Example:
            Create connection context::

                conn = SSHConnection("192.168.1.100", "admin", "secret")
                with conn as ssh:
                    ssh.exec_command("ls /shared")

        .. versionadded:: 0.1.0
        """
        self.ip = ip
        self.username = username
        self.password = password
        self.client = None

    def __enter__(self):
        """Establish SSH connection when entering context.

        Creates a paramiko SSHClient, configures it to auto-accept unknown host keys,
        and establishes the connection using password authentication.

        :return: Connected paramiko SSHClient instance
        :rtype: paramiko.SSHClient
        :raises SSHAuthError: If authentication fails

        Example:
            Context manager automatically calls this::

                with SSHConnection("192.168.1.100", "admin", "password") as ssh:
                    # ssh is the return value from __enter__
                    stdin, stdout, stderr = ssh.exec_command("pwd")

        Note:
            Host key verification is disabled (AutoAddPolicy). Key-based authentication
            is also disabled (look_for_keys=False, allow_agent=False).

        .. versionadded:: 0.1.0
        """
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        try:
            self.client.connect(
                hostname=self.ip,
                username=self.username,
                password=self.password,
                look_for_keys=False,
                allow_agent=False
            )
        except AuthenticationException as e:
            raise SSHAuthError(f"Authentication failed for {self.username}@{self.ip}") from e
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close SSH connection when exiting context.

        Ensures the SSH connection is properly closed, releasing resources. This is
        called automatically when exiting the context manager, even if an exception occurred.

        :param exc_type: Exception type if an exception was raised in the context
        :type exc_type: type | None
        :param exc_val: Exception value if an exception was raised in the context
        :type exc_val: BaseException | None
        :param exc_tb: Exception traceback if an exception was raised in the context
        :type exc_tb: types.TracebackType | None
        :return: False to propagate any exceptions that occurred in the context
        :rtype: bool

        Example:
            Automatic cleanup even with exceptions::

                try:
                    with SSHConnection("192.168.1.100", "admin", "password") as ssh:
                        ssh.exec_command("invalid command that might fail")
                        raise ValueError("Something went wrong")
                except ValueError:
                    # Connection is still properly closed
                    pass

        .. versionadded:: 0.1.0
        """
        if self.client:
            self.client.close()
        return False


def validate_remote_storage(ssh_client, folder_path="/shared/images", min_gb=5):
    """Validate that a remote folder exists and has sufficient disk space available.

    This function checks two conditions on the remote system:
    1. The specified folder path exists
    2. The filesystem containing the folder has at least min_gb gigabytes of free space

    The disk space check uses the 'df' command to determine available space on the
    mount point containing the folder. For example, if folder_path is "/shared/images",
    it checks the available space on the "/shared" mount point.

    :param ssh_client: Connected paramiko SSHClient instance for executing remote commands
    :type ssh_client: paramiko.SSHClient
    :param folder_path: Remote folder path to validate (default: /shared/images)
    :type folder_path: str
    :param min_gb: Minimum required free disk space in gigabytes (default: 5)
    :type min_gb: int | float
    :raises RemoteStorageError: If folder doesn't exist, insufficient disk space, or unable to determine space

    Example:
        Validate storage before file transfer::

            from swimlib.ssh_connect import SSHConnection, validate_remote_storage

            with SSHConnection("192.168.1.100", "admin", "password") as ssh:
                # Ensure 20GB free on /shared/images
                validate_remote_storage(ssh, "/shared/images", min_gb=20)
                print("Storage validation passed")

        Handle validation failures::

            from swimlib.ssh_connect import RemoteStorageError

            try:
                validate_remote_storage(ssh_client, "/nonexistent", min_gb=10)
            except RemoteStorageError as e:
                print(f"Validation failed: {e}")

    Note:
        The function extracts the mount point from the folder path by taking the first
        path component after the root. For example:
        - "/shared/images" -> checks "/shared"
        - "/var/tmp/files" -> checks "/var"

    .. versionadded:: 0.1.0
    """
    # Check folder exists
    stdin, stdout, stderr = ssh_client.exec_command(f"test -d {folder_path} && echo exists")
    if stdout.read().decode().strip() != "exists":
        raise RemoteStorageError(f"Remote folder does not exist: {folder_path}")

    # Extract mount point from folder path (e.g., /shared/images -> /shared)
    mount_point = "/" + folder_path.lstrip("/").split("/")[0]

    # Check disk space
    stdin, stdout, stderr = ssh_client.exec_command(f"df -BG {mount_point} | tail -1 | awk '{{print $4}}'")
    output = stdout.read().decode().strip()

    if not output:
        raise RemoteStorageError(f"Unable to determine disk space for {mount_point}")

    available_gb = float(output.rstrip('G'))
    if available_gb < min_gb:
        raise RemoteStorageError(
            f"Insufficient disk space on {mount_point}: {available_gb}GB available, {min_gb}GB required"
        )
