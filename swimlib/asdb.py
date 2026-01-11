"""ASDB API Client Module.

This module provides a comprehensive HTTP client for interacting with the ASDB
(Automated Software Database) API. It supports both production and local testing modes,
device execution lifecycle management, logging, and history tracking.

The module implements exception-based error handling patterns and supports graceful
degradation when API calls fail.

Classes:
    ASDBClient: HTTP client for ASDB API operations with device context support.

Environment Variables:
    ASDB_BASE_URL (str): Base URL for the ASDB API endpoint (required for remote mode).
    ASDB_TOKEN (str): API authentication token (required for remote mode).
    ASDB_MODE (str): Operation mode - 'remote' for production API calls or 'local' for dry-run logging only. Defaults to 'remote'.

Example:
    Basic client initialization and usage::

        from swimlib.asdb import ASDBClient

        # Initialize with environment variables
        client = ASDBClient()

        # Initialize with explicit parameters
        client = ASDBClient(
            base_url="https://asdb.example.com",
            api_token="your-api-token",
            mode="remote"
        )

        # Update execution status
        client.update_execution_log_status("log-123", "inprogress")

        # Send log entry
        client.send_log("Starting device validation", log_level="info")

Note:
    This is a legacy implementation. See CLAUDE.md for the newer refactored version
    with ``ASDBClient.from_env()`` and ``ExecutionContext`` patterns.

Warning:
    This implementation calls ``sys.exit()`` on failures, which conflicts with the
    library design goal of exception-based error handling. This should be refactored
    to raise ``ASDBError`` exceptions instead.

See Also:
    - :mod:`swimlib.ssh_connect` for SSH connection management
    - :mod:`swimlib.f5.run` for F5 upgrade workflow orchestration

.. versionadded:: 0.1.0
"""
from datetime import datetime
from swimlib import log
import os
import sys
import requests
from typing import Any, Dict, Optional, Union


class ASDBClient:
    """HTTP client for interacting with ASDB API and managing device execution lifecycles.

    This class provides a comprehensive interface to the ASDB API, supporting both
    production ('remote') and testing ('local') modes. In remote mode, it makes actual
    HTTP API calls. In local mode, it logs the operations without making network requests.

    The client maintains a device context dictionary that tracks execution metadata and
    automatically updates execution status upon initialization if an execution_log_id is present.

    :ivar device: Device context dictionary containing execution metadata.
    :vartype device: Dict[str, Any]
    :ivar base_url: Base URL for ASDB API endpoint.
    :vartype base_url: str
    :ivar api_token: API authentication token.
    :vartype api_token: str
    :ivar mode: Operation mode - 'remote' or 'local'.
    :vartype mode: str
    :ivar headers: HTTP headers for API requests including authorization.
    :vartype headers: Dict[str, str]

    Example:
        Initialize client and update execution status::

            client = ASDBClient(
                base_url="https://asdb.example.com",
                api_token="token123",
                device={"execution_log_id": "log-456", "device_name": "router-01"},
                mode="remote"
            )

            # Client automatically updates status to 'inprogress' on init
            client.send_log("Starting upgrade process", log_level="info")

    .. warning::
        Initialization will call ``sys.exit(1)`` if the automatic status update fails.
        This behavior should be refactored to raise exceptions instead.

    .. versionadded:: 0.1.0
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_token: str | None = None,
        device: Dict[str, Any] | None = None,
        mode: str | None = None,
    ) -> None:
        """Initialize ASDB client with URL, authentication token, optional device context, and operation mode.

        The client reads configuration from environment variables if not explicitly provided.
        If a device context with an execution_log_id is provided, the client automatically
        updates the execution status to 'inprogress' upon initialization.

        :param base_url: Base URL for ASDB API. If None, reads from ASDB_BASE_URL environment variable.
        :type base_url: str | None
        :param api_token: API authentication token. If None, reads from ASDB_TOKEN environment variable.
        :type api_token: str | None
        :param device: Device context dictionary containing execution metadata such as execution_log_id,
            device_name, execution_type, etc. Defaults to empty dict if None.
        :type device: Dict[str, Any] | None
        :param mode: Operation mode - 'remote' for production API calls or 'local' for dry-run logging.
            If None, reads from ASDB_MODE environment variable (defaults to 'remote').
        :type mode: str | None
        :raises SystemExit: If automatic execution status update fails during initialization.

        Example:
            Initialize with explicit parameters::

                client = ASDBClient(
                    base_url="https://asdb.example.com",
                    api_token="my-token",
                    device={"execution_log_id": "log-123"},
                    mode="remote"
                )

            Initialize from environment variables::

                # Set environment: ASDB_BASE_URL, ASDB_TOKEN, ASDB_MODE
                client = ASDBClient()

        .. note::
            The automatic status update on initialization may not be desirable in all use cases.
            Consider refactoring to make this behavior explicit rather than implicit.

        .. versionadded:: 0.1.0
        """
        self.device = device or {}
        self.base_url = base_url or os.getenv("ASDB_BASE_URL")
        self.api_token = api_token or os.getenv("ASDB_TOKEN")
        self.mode = (mode or os.getenv("ASDB_MODE", "remote")).lower()
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Token {self.api_token}",
        }

        try:
            exec_id = self.device.get("execution_log_id")
            if exec_id:
                self.update_execution_log_status(exec_id, "inprogress")
        except Exception as exc:
            self.fail_device_execution(f"Error: Failed to initialize ASDB client: {exc}")

    def _make_request(self, method: str, endpoint: str, payload: Dict | None = None) -> Optional[requests.Response]:
        """Make HTTP request to ASDB API with automatic mode handling.

        This internal method handles all HTTP communication with the ASDB API. In 'remote'
        mode, it makes actual HTTP requests. In 'local' mode, it logs the request details
        without making network calls, which is useful for testing and dry-run scenarios.

        :param method: HTTP method verb (GET, POST, PATCH, PUT, DELETE, etc.)
        :type method: str
        :param endpoint: API endpoint path relative to base_url (leading slash optional)
        :type endpoint: str
        :param payload: Request payload data to send as JSON body
        :type payload: Dict[str, Any] | None
        :return: Response object from requests library in remote mode, None in local mode
        :rtype: requests.Response | None

        Example:
            Make a PATCH request to update execution status::

                response = client._make_request(
                    method="PATCH",
                    endpoint="swimv2/execution_log/log-123/",
                    payload={"execution_status": "completed"}
                )

        .. note::
            SSL verification is disabled (``verify=False``). This should be configurable
            in production environments that require certificate validation.

        .. warning::
            This is an internal method. Use the public API methods like
            ``update_execution_log_status()`` instead.

        .. versionadded:: 0.1.0
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if self.mode == "local":
            log.info(f"[ASDB local] {method} {url} payload={payload}")
            return None
        return requests.request(method=method, url=url, json=payload, headers=self.headers, verify=False)

    def update_execution_log_status(self, execution_log_id: str, status: str) -> Optional[requests.Response]:
        """Update the execution status of a specific execution log in ASDB.

        This method sends a PATCH request to update the execution_status field of an
        execution log. Common status values include 'inprogress', 'completed', and 'failed'.

        :param execution_log_id: Unique identifier of the execution log to update
        :type execution_log_id: str
        :param status: New execution status value (e.g., 'inprogress', 'completed', 'failed')
        :type status: str
        :return: Response object from the API request, or None in local mode
        :rtype: requests.Response | None

        Example:
            Update execution log to completed status::

                client = ASDBClient()
                response = client.update_execution_log_status("log-456", "completed")

        .. seealso::
            - :meth:`send_log` for appending log entries to the execution log

        .. versionadded:: 0.1.0
        """
        endpoint = f"swimv2/execution_log/{execution_log_id}/"
        payload = {"execution_status": status}
        return self._make_request("PATCH", endpoint, payload)

    def send_log(self, message: str, log_level: str = "info") -> Optional[requests.Response]:
        """Append a log entry to the execution log using the device context.

        This method sends a timestamped log entry to ASDB. It uses the execution_log_id
        from the device context dictionary. If no execution_log_id is available, the
        method logs a warning and returns None without making an API call.

        :param message: Log message text to send to ASDB
        :type message: str
        :param log_level: Severity level of the log entry (info, warning, error, debug)
        :type log_level: str
        :return: Response object from the API request, or None if no execution_log_id or in local mode
        :rtype: requests.Response | None

        Example:
            Send log entries at different severity levels::

                client = ASDBClient(device={"execution_log_id": "log-123"})
                client.send_log("Starting device upgrade", log_level="info")
                client.send_log("Warning: High memory usage detected", log_level="warning")
                client.send_log("Failed to connect to device", log_level="error")

        .. warning::
            Requires device context with execution_log_id to be set during initialization.
            Will log a warning and return None if execution_log_id is not available.

        .. versionadded:: 0.1.0
        """
        exec_id = self.device.get("execution_log_id")
        if not exec_id:
            log.warning("ASDBClient.send_log called without device or execution_log_id")
            return None
        endpoint = f"swimv2/execution_log/{exec_id}/append_log/"
        payload = [{"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "message": message, "log_level": log_level}]
        return self._make_request("POST", endpoint, payload)

    def pre_validation_status(self, conn_status: str) -> Optional[requests.Response]:
        """Update device connection status in ASDB.

        This method updates the conn_status field for a device, typically used during
        pre-validation checks to indicate connectivity and authentication status.

        :param conn_status: Connection status value (e.g., 'pass', 'fail', 'fail_auth', 'disk_full')
        :type conn_status: str
        :return: Response object from the API request, or None if no device_name or in local mode
        :rtype: requests.Response | None

        Example:
            Update device connection status after validation::

                client = ASDBClient(device={"device_name": "router-01"})
                client.pre_validation_status("pass")

        .. warning::
            Requires device context with device_name to be set during initialization.
            Will log a warning and return None if device_name is not available.

        .. seealso::
            - :class:`swimlib.f5.run.PreValStatus` for common status values

        .. versionadded:: 0.1.0
        """
        device_name = self.device.get("device_name")
        if not device_name:
            log.warning("ASDBClient.pre_validation_status called without device.device_name")
            return None
        endpoint = f"swimv2/devices/{device_name}/"
        payload = {"conn_status": conn_status}
        return self._make_request("PATCH", endpoint, payload)

    def send_device_history(self, status: str = "completed") -> Optional[requests.Response]:
        """Create a device history record in ASDB based on execution type.

        This method creates a history record to track device upgrade progress and outcomes.
        It automatically skips history creation for 'dry_run' execution types, as those are
        validation-only operations that should not be permanently recorded.

        The history record includes metadata about the upgrade process, built using the
        build_history_metadata() method.

        :param status: History record status (e.g., 'completed', 'failed')
        :type status: str
        :return: Response object from the API request, or None for dry_run executions or in local mode
        :rtype: requests.Response | None

        Example:
            Send successful completion history::

                client = ASDBClient(device={
                    "execution_id": "exec-789",
                    "device_name": "router-01",
                    "execution_type": "image_upgrade",
                    "target_version": "21.0.0"
                })
                client.send_device_history(status="completed")

        .. note::
            Automatically returns None for dry_run execution types without making an API call.

        .. seealso::
            - :meth:`build_history_metadata` for metadata structure details

        .. versionadded:: 0.1.0
        """
        etype = self.device.get("execution_type")
        if etype == "dry_run":
            return None

        target_version = self.device.get("target_version")
        metadata = self.build_history_metadata(target_version, status)

        endpoint = "swimv2/device_history/"
        payload = {
            "request_id_input": self.device.get("execution_id"),
            "device_input": self.device.get("device_name"),
            "stage": etype,
            "metadata": metadata,
        }
        return self._make_request("POST", endpoint, payload)

    def build_history_metadata(self, target_version: str | None, status: str) -> Dict[str, Any]:
        """Build standardized metadata dictionary for device history records.

        Constructs a comprehensive metadata structure containing information about the
        BIG-IP software upgrade, including image details, volume information, checksums,
        and change request references.

        :param target_version: Target software version for the upgrade (e.g., "21.0.0")
        :type target_version: str | None
        :param status: Upload/upgrade status (e.g., 'completed', 'failed')
        :type status: str
        :return: Metadata dictionary with standardized BIG-IP upgrade fields
        :rtype: Dict[str, Any]

        Example:
            Build metadata for a completed upgrade::

                metadata = client.build_history_metadata("21.0.0", "completed")
                # Returns: {
                #     "image_name": "BIGIP-21.0.0.iso",
                #     "version": "21.0.0",
                #     "volume": "HD1.1",
                #     "upload_status": "completed",
                #     ...
                # }

        .. note::
            Some fields contain placeholder values (e.g., CR numbers "CR12345678", "CR12345")
            that should be replaced with actual change request identifiers in production.

            The current_version defaults to "17.X" and should be made configurable.

        .. seealso::
            - :meth:`send_device_history` which uses this method to build metadata

        .. versionadded:: 0.1.0
        """
        tv = target_version or ""
        return {
            "image_name": f"BIGIP-{tv}.iso",
            "version": tv,
            "volume": "HD1.1",
            "upload_status": status,
            "cr_image_copy": "CR12345678",
            "source_location": self.device.get("local_folder"),
            "destination_location": self.device.get("remote_folder"),
            "cr_image_stage": "CR12345",
            "current_version": "17.X",
            "current_volume": "HD1.1",
            "target_version": tv,
            "target_volume": "HD1.2",
            "checksum_status": True,
        }

    def resolve_execution(self, message: str) -> None:
        """Resolve execution outcome based on execution type - pass for dry_run, fail otherwise.

        This method provides conditional execution resolution: for 'dry_run' execution types,
        it calls pass_device_execution() which exits with code 0. For all other execution types,
        it calls fail_device_execution() which exits with code 1.

        This pattern allows validation workflows to complete successfully while treating
        production workflow errors as failures.

        :param message: Message to log and send to ASDB explaining the resolution reason
        :type message: str
        :raises SystemExit: Always raises SystemExit (code 0 for dry_run, code 1 otherwise)

        Example:
            Handle validation errors differently based on execution type::

                try:
                    validate_device_config(device)
                except ValidationError as e:
                    # Exits with code 0 for dry_run, code 1 for production
                    client.resolve_execution(f"Validation failed: {e}")

        .. warning::
            This method always calls sys.exit() and never returns. Consider refactoring
            to raise exceptions instead of terminating the process.

        .. seealso::
            - :meth:`pass_device_execution` for successful completion handling
            - :meth:`fail_device_execution` for failure handling

        .. versionadded:: 0.1.0
        """
        exec_type = str(self.device.get("execution_type", "")).lower()
        if exec_type == "dry_run":
            self.pass_device_execution(message)
        else:
            self.fail_device_execution(message)

    def fail_device_execution(self, message: str) -> None:
        """Mark device execution as failed, update ASDB, and terminate process with error code.

        This method performs a complete failure workflow:
        1. Logs the error message locally
        2. Sends the error log to ASDB
        3. Updates execution log status to 'failed'
        4. Creates a failed device history record
        5. Exits the process with code 1

        :param message: Error message explaining the failure reason
        :type message: str
        :raises SystemExit: Always exits with code 1 after updating ASDB

        Example:
            Handle critical failure::

                if not device_reachable:
                    client.fail_device_execution("Device unreachable: connection timeout")
                # Process terminates here - code below never executes

        .. warning::
            This method always calls sys.exit(1) and never returns. This violates the
            library design principle of exception-based error handling. Should be refactored
            to raise ASDBError exceptions instead, letting the caller decide whether to exit.

        .. seealso::
            - :meth:`pass_device_execution` for successful completion
            - :meth:`resolve_execution` for conditional resolution based on execution type

        .. versionadded:: 0.1.0
        """
        log.error(message)
        self.send_log(message, log_level="error")
        exec_log_id = self.device.get("execution_log_id")
        if exec_log_id:
            self.update_execution_log_status(exec_log_id, "failed")
        self.send_device_history("failed")
        sys.exit(1)

    def pass_device_execution(self, message: str, status: str = "completed") -> None:
        """Mark device execution as completed, update ASDB, and terminate process successfully.

        This method performs a complete success workflow:
        1. Sends the success message to ASDB as an info-level log
        2. Updates execution log status (defaults to 'completed')
        3. Creates a device history record with the specified status
        4. Exits the process with code 0

        :param message: Success message explaining the completion outcome
        :type message: str
        :param status: Execution status to set (defaults to 'completed')
        :type status: str
        :raises SystemExit: Always exits with code 0 after updating ASDB

        Example:
            Mark successful completion::

                client.pass_device_execution("Device upgrade completed successfully")
                # Process terminates here - code below never executes

            Mark completion with custom status::

                client.pass_device_execution(
                    "Pre-validation checks passed",
                    status="validated"
                )

        .. warning::
            This method always calls sys.exit(0) and never returns. This violates the
            library design principle of exception-based error handling. Should be refactored
            to return normally instead, letting the caller decide whether to exit.

        .. seealso::
            - :meth:`fail_device_execution` for failure handling
            - :meth:`resolve_execution` for conditional resolution based on execution type

        .. versionadded:: 0.1.0
        """
        self.send_log(message, log_level="info")
        exec_log_id = self.device.get("execution_log_id")
        if exec_log_id:
            self.update_execution_log_status(exec_log_id, status)
        self.send_device_history(status)
        sys.exit(0)
