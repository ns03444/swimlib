"""SSH Connection Manager for F5 BIG-IP Devices"""

from paramiko import SSHClient, AutoAddPolicy, AuthenticationException


class SSHAuthError(Exception):
    """Custom exception for SSH authentication failures."""
    pass


class RemoteStorageError(Exception):
    """Custom exception for remote storage validation failures."""
    pass


class SSHConnection:
    """
    Simple SSH client with context manager support.

    Usage:
        with SSHConnection(ip, username, password) as ssh:
            stdin, stdout, stderr = ssh.exec_command("tmsh show sys version")
            output = stdout.read().decode()
    """

    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password
        self.client = None

    def __enter__(self):
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
        if self.client:
            self.client.close()
        return False


def validate_remote_storage(ssh_client, folder_path="/shared/images", min_gb=5):
    """
    Validate remote storage folder exists and has sufficient disk space.

    Args:
        ssh_client: Connected Paramiko SSHClient instance
        folder_path: Path to validate (default: /shared/images)
        min_gb: Minimum required space in GB (default: 5)

    Raises:
        RemoteStorageError: If folder doesn't exist or insufficient disk space
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
