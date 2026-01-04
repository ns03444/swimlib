from datetime import datetime
from swimlib import log
import os
import sys
import requests
from typing import Any, Dict, Optional, Union


class ASDBClient:
    """Client for interacting with ASDB API and providing action helpers."""

    def __init__(
        self,
        base_url: str | None = None,
        api_token: str | None = None,
        device: Dict[str, Any] | None = None,
        mode: str | None = None,
    ) -> None:
        """Initialize ASDB client with URL, authentication token, optional device, and mode.

        :param base_url: Base URL for ASDB API (defaults to env variable or hardcoded)
        :type base_url: str | None
        :param api_token: API token for authentication (defaults to env variable)
        :type api_token: str | None
        :param device: Optional device context as dictionary
        :type device: dict | None
        :param mode: Operation mode ("local" or "remote", defaults to env or "remote")
        :type mode: str | None
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
        """Make HTTP request to ASDB API.

        :param method: HTTP method (GET, POST, PATCH, etc.)
        :type method: str
        :param endpoint: API endpoint path
        :type endpoint: str
        :param payload: Request payload data
        :type payload: dict | None
        :return: Response object from requests (None in local mode)
        :rtype: requests.Response | None
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if self.mode == "local":
            log.info(f"[ASDB local] {method} {url} payload={payload}")
            return None
        return requests.request(method=method, url=url, json=payload, headers=self.headers, verify=False)

    def update_execution_log_status(self, execution_log_id: str, status: str) -> Optional[requests.Response]:
        """Update execution log status.

        :param execution_log_id: ID of the execution log
        :type execution_log_id: str
        :param status: New status value
        """
        endpoint = f"swimv2/execution_log/{execution_log_id}/"
        payload = {"execution_status": status}
        return self._make_request("PATCH", endpoint, payload)

    def send_log(self, message: str, log_level: str = "info") -> Optional[requests.Response]:
        """Append log entry to execution log using the device context."""
        exec_id = self.device.get("execution_log_id")
        if not exec_id:
            log.warning("ASDBClient.send_log called without device or execution_log_id")
            return None
        endpoint = f"swimv2/execution_log/{exec_id}/append_log/"
        payload = [{"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "message": message, "log_level": log_level}]
        return self._make_request("POST", endpoint, payload)

    def pre_validation_status(self, conn_status: str) -> Optional[requests.Response]:
        """Update device connection status."""
        device_name = self.device.get("device_name")
        if not device_name:
            log.warning("ASDBClient.pre_validation_status called without device.device_name")
            return None
        endpoint = f"swimv2/devices/{device_name}/"
        payload = {"conn_status": conn_status}
        return self._make_request("PATCH", endpoint, payload)

    def send_device_history(self, status: str = "completed") -> Optional[requests.Response]:
        """Send device history record based on execution type."""
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
        """Build metadata dictionary for device history."""
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
        """Pass execution on dry-run; fail otherwise (based on device.execution_type)"""
        exec_type = str(self.device.get("execution_type", "")).lower()
        if exec_type == "dry_run":
            self.pass_device_execution(message)
        else:
            self.fail_device_execution(message)

    def fail_device_execution(self, message: str) -> None:
        """Mark execution as failed, log error, update history, and exit."""
        log.error(message)
        self.send_log(message, log_level="error")
        exec_log_id = self.device.get("execution_log_id")
        if exec_log_id:
            self.update_execution_log_status(exec_log_id, "failed")
        self.send_device_history("failed")
        sys.exit(1)

    def pass_device_execution(self, message: str, status: str = "completed") -> None:
        """Mark execution as completed, log success, update history, and exit."""
        self.send_log(message, log_level="info")
        exec_log_id = self.device.get("execution_log_id")
        if exec_log_id:
            self.update_execution_log_status(exec_log_id, status)
        self.send_device_history(status)
        sys.exit(0)
