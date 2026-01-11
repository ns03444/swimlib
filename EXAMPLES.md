# swimlib Code Examples

[![Guides](https://img.shields.io/badge/docs-guides-blue.svg)](GUIDES.md)
[![Examples](https://img.shields.io/badge/code-examples-green.svg)](EXAMPLES.md)

Practical code examples demonstrating swimlib usage patterns.

---

## Table of Contents

- [Basic Usage](#-basic-usage)
- [CLI Applications](#-cli-applications)
- [Advanced Workflows](#-advanced-workflows)
- [Error Handling](#-error-handling)
- [Testing Examples](#-testing-examples)
- [Real-World Scenarios](#-real-world-scenarios)

---

## 🎯 Basic Usage

### Example 1: Simple Execution

```python
"""
Simple execution tracking example.
Demonstrates the basic lifecycle: start → log → complete
"""

from swimlib.asdb import ASDBClient, ExecutionContext, ASDBError
import sys

def main():
    try:
        # Initialize client from environment
        client = ASDBClient.from_env()

        # Create execution context
        ctx = ExecutionContext(
            client=client,
            device_name="router-01.prod.company.com",
            execution_id="exec-2026-001",
            execution_log_id="log-2026-001",
            execution_type="production"
        )

        # Start execution
        ctx.start()
        ctx.log("Execution started successfully", "info")

        # Simulate work
        ctx.log("Processing configuration...", "info")
        # ... your logic here ...

        # Complete execution
        ctx.complete("Execution completed successfully", {})

    except ASDBError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Example 2: Using Metadata

```python
"""
Demonstrates using structured metadata for upgrade operations.
"""

from swimlib.asdb import (
    ASDBClient,
    ExecutionContext,
    build_upgrade_metadata,
    ASDBError
)

def upgrade_with_metadata():
    client = ASDBClient.from_env()
    ctx = ExecutionContext(
        client=client,
        device_name="bigip-01.company.com",
        execution_id="upgrade-001",
        execution_log_id="log-001",
        execution_type="production"
    )

    ctx.start()

    # Build structured metadata
    metadata = build_upgrade_metadata(
        target_version="18.1.0",
        local_folder="/opt/images",
        remote_folder="/shared/images",
        image_name="BIGIP-18.1.0-0.0.123.iso",
        current_version="17.1.0",  # Optional, defaults to "17.X"
        md5_local="a1b2c3d4e5f6...",
        md5_remote="a1b2c3d4e5f6...",
        cr_number="CR-2026-001"
    )

    ctx.log("Upgrade metadata prepared", "info")
    ctx.complete("Upgrade successful", metadata)

if __name__ == "__main__":
    try:
        upgrade_with_metadata()
    except ASDBError as e:
        print(f"Upgrade failed: {e}")
        sys.exit(1)
```

### Example 3: Local Mode Testing

```python
"""
Run workflows in local mode without making API calls.
Perfect for development and testing.
"""

import os
from swimlib.asdb import ASDBClient, ExecutionContext

def test_workflow_locally():
    # Force local mode
    os.environ['ASDB_MODE'] = 'local'

    client = ASDBClient.from_env()
    ctx = ExecutionContext(
        client=client,
        device_name="test-device.local",
        execution_id="test-exec",
        execution_log_id="test-log",
        execution_type="dry_run"
    )

    # These will only log to console, no API calls
    ctx.start()
    ctx.log("Testing workflow logic...", "info")
    ctx.log("All validations passed", "info")
    ctx.complete("Test completed", {})

    print("✓ Local test completed successfully")

if __name__ == "__main__":
    test_workflow_locally()
```

---

## 💻 CLI Applications

### Example 4: Basic CLI Tool

```python
#!/usr/bin/env python3
"""
cli_upgrade.py - Simple CLI tool for device upgrades
Usage: python cli_upgrade.py <device_name> <execution_id> <log_id>
"""

import sys
import argparse
from swimlib.asdb import ASDBClient, ExecutionContext, ASDBError
from swimlib import log

def parse_args():
    parser = argparse.ArgumentParser(description="Device upgrade CLI")
    parser.add_argument("device_name", help="Target device FQDN")
    parser.add_argument("execution_id", help="ASDB execution ID")
    parser.add_argument("log_id", help="ASDB log ID")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode"
    )
    return parser.parse_args()

def run_upgrade(device_name, execution_id, log_id, dry_run=False):
    """Execute the upgrade workflow."""
    try:
        client = ASDBClient.from_env()

        exec_type = "dry_run" if dry_run else "production"
        ctx = ExecutionContext(
            client=client,
            device_name=device_name,
            execution_id=execution_id,
            execution_log_id=log_id,
            execution_type=exec_type
        )

        ctx.start()
        log.info(f"Starting upgrade for {device_name}")

        # Your upgrade logic here
        ctx.log("Connecting to device...", "info")
        ctx.log("Uploading image...", "info")
        ctx.log("Installing software...", "info")

        ctx.complete("Upgrade completed successfully", {})
        return 0

    except ASDBError as e:
        log.error(f"Upgrade failed: {e}")
        return 1

def main():
    args = parse_args()

    exit_code = run_upgrade(
        args.device_name,
        args.execution_id,
        args.log_id,
        args.dry_run
    )

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
```

**Usage:**

```bash
# Production run
python cli_upgrade.py router-01.prod exec-123 log-456

# Dry-run
python cli_upgrade.py router-01.prod exec-123 log-456 --dry-run
```

### Example 5: Advanced CLI with Progress

```python
#!/usr/bin/env python3
"""
advanced_cli.py - CLI with progress tracking and error recovery
"""

import sys
import time
from typing import Optional
from swimlib.asdb import ASDBClient, ExecutionContext, ASDBError
from swimlib import log

class UpgradeWorkflow:
    """Encapsulates upgrade workflow with progress tracking."""

    def __init__(self, ctx: ExecutionContext, device_name: str):
        self.ctx = ctx
        self.device_name = device_name
        self.steps = [
            ("Validating prerequisites", self.validate),
            ("Uploading image", self.upload),
            ("Installing software", self.install),
            ("Verifying installation", self.verify),
        ]

    def validate(self):
        """Validate prerequisites."""
        self.ctx.log("Checking device connectivity...", "info")
        time.sleep(1)  # Simulate work
        self.ctx.log("Checking disk space...", "info")
        time.sleep(1)
        self.ctx.log("✓ Prerequisites validated", "info")

    def upload(self):
        """Upload image to device."""
        self.ctx.log("Starting SFTP transfer...", "info")
        time.sleep(2)  # Simulate upload
        self.ctx.log("Verifying MD5 checksum...", "info")
        time.sleep(1)
        self.ctx.log("✓ Image uploaded successfully", "info")

    def install(self):
        """Install software."""
        self.ctx.log("Installing to inactive volume...", "info")
        time.sleep(3)  # Simulate installation
        self.ctx.log("✓ Installation complete", "info")

    def verify(self):
        """Verify installation."""
        self.ctx.log("Verifying software integrity...", "info")
        time.sleep(1)
        self.ctx.log("✓ Verification passed", "info")

    def run(self) -> bool:
        """Execute all workflow steps."""
        total = len(self.steps)

        for idx, (step_name, step_func) in enumerate(self.steps, 1):
            try:
                self.ctx.log(
                    f"[{idx}/{total}] {step_name}...",
                    "info"
                )
                step_func()

            except Exception as e:
                self.ctx.log(
                    f"✗ Step failed: {step_name} - {e}",
                    "error"
                )
                return False

        return True

def main():
    if len(sys.argv) != 4:
        print("Usage: advanced_cli.py <device> <exec_id> <log_id>")
        sys.exit(1)

    device_name = sys.argv[1]
    execution_id = sys.argv[2]
    log_id = sys.argv[3]

    try:
        client = ASDBClient.from_env()
        ctx = ExecutionContext(
            client=client,
            device_name=device_name,
            execution_id=execution_id,
            execution_log_id=log_id,
            execution_type="production"
        )

        ctx.start()
        log.info(f"Starting upgrade workflow for {device_name}")

        workflow = UpgradeWorkflow(ctx, device_name)
        success = workflow.run()

        if success:
            ctx.complete("Upgrade completed successfully", {})
            log.info("✓ All steps completed")
            sys.exit(0)
        else:
            ctx.fail("Upgrade failed during execution", {})

    except ASDBError as e:
        log.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 🔄 Advanced Workflows

### Example 6: Multi-Stage Workflow

```python
"""
Multi-stage workflow with checkpoints and rollback capability.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from swimlib.asdb import ASDBClient, ExecutionContext, ASDBError
from swimlib import log

@dataclass
class WorkflowStage:
    """Represents a workflow stage."""
    name: str
    stage_id: str
    metadata: Dict[str, Any]

class MultiStageWorkflow:
    """Manages multi-stage execution with ASDB tracking."""

    def __init__(self, ctx: ExecutionContext):
        self.ctx = ctx
        self.completed_stages: List[str] = []

    def execute_stage(self, stage: WorkflowStage) -> bool:
        """Execute a single stage with tracking."""
        try:
            self.ctx.log(f"Starting stage: {stage.name}", "info")

            # Create stage history in ASDB
            if self.ctx.execution_type == "production":
                self.ctx.client.create_device_history(
                    execution_id=self.ctx.execution_id,
                    device_name=self.ctx.device_name,
                    stage=stage.stage_id,
                    metadata=stage.metadata
                )

            # Simulate stage work
            self._perform_stage_work(stage)

            self.completed_stages.append(stage.name)
            self.ctx.log(f"✓ Completed stage: {stage.name}", "info")
            return True

        except Exception as e:
            self.ctx.log(f"✗ Stage failed: {stage.name} - {e}", "error")
            return False

    def _perform_stage_work(self, stage: WorkflowStage):
        """Placeholder for actual stage work."""
        # Implement stage-specific logic here
        pass

    def rollback(self):
        """Rollback completed stages."""
        self.ctx.log("Initiating rollback...", "warning")

        for stage_name in reversed(self.completed_stages):
            self.ctx.log(f"Rolling back: {stage_name}", "warning")
            # Implement rollback logic

        self.ctx.log("Rollback complete", "info")

def run_multistage_upgrade():
    """Execute multi-stage upgrade workflow."""
    client = ASDBClient.from_env()
    ctx = ExecutionContext(
        client=client,
        device_name="bigip-cluster-01",
        execution_id="multi-001",
        execution_log_id="log-001",
        execution_type="production"
    )

    ctx.start()
    workflow = MultiStageWorkflow(ctx)

    stages = [
        WorkflowStage(
            name="Backup Configuration",
            stage_id="backup",
            metadata={"backup_path": "/var/backup/config.ucs"}
        ),
        WorkflowStage(
            name="Upload Image",
            stage_id="upload",
            metadata={"image": "BIGIP-18.1.0.iso", "size_mb": 2048}
        ),
        WorkflowStage(
            name="Install Software",
            stage_id="install",
            metadata={"volume": "HD1.2", "version": "18.1.0"}
        ),
        WorkflowStage(
            name="Reboot Device",
            stage_id="reboot",
            metadata={"active_volume": "HD1.2"}
        ),
    ]

    try:
        for stage in stages:
            if not workflow.execute_stage(stage):
                workflow.rollback()
                ctx.fail("Workflow failed, rolled back", {})
                return

        ctx.complete("Multi-stage upgrade completed", {
            "stages_completed": len(workflow.completed_stages)
        })

    except ASDBError as e:
        log.error(f"Fatal error: {e}")
        workflow.rollback()
        raise

if __name__ == "__main__":
    try:
        run_multistage_upgrade()
    except ASDBError as e:
        log.error(f"Upgrade failed: {e}")
        sys.exit(1)
```

### Example 7: Parallel Device Operations

```python
"""
Execute operations on multiple devices in parallel.
"""

import concurrent.futures
from typing import List, Tuple
from swimlib.asdb import ASDBClient, ExecutionContext, ASDBError
from swimlib import log

def upgrade_device(
    device_name: str,
    execution_id: str,
    log_id: str
) -> Tuple[str, bool, str]:
    """
    Upgrade a single device.
    Returns: (device_name, success, message)
    """
    try:
        client = ASDBClient.from_env()
        ctx = ExecutionContext(
            client=client,
            device_name=device_name,
            execution_id=execution_id,
            execution_log_id=log_id,
            execution_type="production"
        )

        ctx.start()
        ctx.log("Starting device upgrade", "info")

        # Simulate upgrade work
        # ... your upgrade logic ...

        ctx.complete("Upgrade successful", {})
        return (device_name, True, "Success")

    except ASDBError as e:
        return (device_name, False, str(e))

def upgrade_fleet(devices: List[Tuple[str, str, str]], max_workers: int = 5):
    """
    Upgrade multiple devices in parallel.

    Args:
        devices: List of (device_name, execution_id, log_id) tuples
        max_workers: Maximum parallel operations
    """
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = {
            executor.submit(upgrade_device, *device_info): device_info[0]
            for device_info in devices
        }

        # Collect results
        for future in concurrent.futures.as_completed(futures):
            device_name = futures[future]
            try:
                result = future.result()
                results.append(result)

                if result[1]:
                    log.info(f"✓ {result[0]}: {result[2]}")
                else:
                    log.error(f"✗ {result[0]}: {result[2]}")

            except Exception as e:
                log.error(f"✗ {device_name}: Unexpected error - {e}")
                results.append((device_name, False, str(e)))

    # Summary
    successful = sum(1 for r in results if r[1])
    failed = len(results) - successful

    log.info(f"\nUpgrade Summary:")
    log.info(f"  Total: {len(results)}")
    log.info(f"  Successful: {successful}")
    log.info(f"  Failed: {failed}")

    return results

if __name__ == "__main__":
    # Define device fleet
    devices = [
        ("router-01.prod", "exec-001", "log-001"),
        ("router-02.prod", "exec-002", "log-002"),
        ("router-03.prod", "exec-003", "log-003"),
        ("router-04.prod", "exec-004", "log-004"),
        ("router-05.prod", "exec-005", "log-005"),
    ]

    # Upgrade with max 3 parallel operations
    results = upgrade_fleet(devices, max_workers=3)

    # Exit with error if any failed
    if any(not r[1] for r in results):
        sys.exit(1)
```

---

## 🛡️ Error Handling

### Example 8: Comprehensive Error Handling

```python
"""
Demonstrates comprehensive error handling strategies.
"""

import time
from typing import Optional
from swimlib.asdb import ASDBClient, ExecutionContext, ASDBError
from swimlib import log

def retry_operation(func, max_attempts=3, delay=2):
    """Retry wrapper for transient failures."""
    for attempt in range(max_attempts):
        try:
            return func()
        except ASDBError as e:
            if attempt == max_attempts - 1:
                raise
            log.warning(f"Attempt {attempt + 1} failed: {e}")
            log.info(f"Retrying in {delay}s...")
            time.sleep(delay)

def safe_upgrade_with_fallback(
    device_name: str,
    execution_id: str,
    log_id: str
) -> Optional[str]:
    """
    Upgrade with comprehensive error handling and fallback.
    Returns: Success message or None on failure
    """
    client = None
    ctx = None

    try:
        # Initialize with retry
        client = retry_operation(lambda: ASDBClient.from_env())

        ctx = ExecutionContext(
            client=client,
            device_name=device_name,
            execution_id=execution_id,
            execution_log_id=log_id,
            execution_type="production"
        )

        # Start with retry
        retry_operation(lambda: ctx.start())

        # Main workflow
        try:
            ctx.log("Beginning upgrade workflow", "info")

            # Step 1: Validate
            ctx.log("Validating prerequisites...", "info")
            # ... validation logic ...

            # Step 2: Upload
            ctx.log("Uploading image...", "info")
            # ... upload logic ...

            # Step 3: Install
            ctx.log("Installing software...", "info")
            # ... install logic ...

            # Complete successfully
            ctx.complete("Upgrade completed", {})
            return "Upgrade successful"

        except KeyboardInterrupt:
            # Handle user interruption
            log.warning("Upgrade interrupted by user")
            if ctx:
                try:
                    ctx.fail("Upgrade interrupted", {})
                except ASDBError:
                    pass  # Best effort
            return None

        except Exception as e:
            # Handle unexpected errors
            log.error(f"Unexpected error during upgrade: {e}")
            if ctx:
                try:
                    ctx.fail(f"Unexpected error: {e}", {})
                except ASDBError:
                    pass  # Best effort
            return None

    except ASDBError as e:
        # Handle ASDB initialization/communication errors
        log.error(f"ASDB error: {e}")
        log.info("Attempting local-only execution...")

        # Fallback: try to continue without ASDB
        try:
            log.info("Executing upgrade locally without ASDB tracking")
            # ... local-only upgrade logic ...
            log.info("Local upgrade completed (not tracked in ASDB)")
            return "Local upgrade successful (ASDB unavailable)"
        except Exception as local_error:
            log.error(f"Local execution also failed: {local_error}")
            return None

    except Exception as e:
        # Catch-all for truly unexpected errors
        log.error(f"Fatal unexpected error: {e}")
        return None

if __name__ == "__main__":
    result = safe_upgrade_with_fallback(
        "router-01.prod",
        "exec-123",
        "log-456"
    )

    if result:
        log.info(f"✓ {result}")
        sys.exit(0)
    else:
        log.error("✗ Upgrade failed")
        sys.exit(1)
```

### Example 9: Graceful Degradation

```python
"""
Graceful degradation when ASDB is unavailable.
"""

from swimlib.asdb import ASDBClient, ExecutionContext, ASDBError
from swimlib import log

class ResilientExecutor:
    """Executor that gracefully handles ASDB unavailability."""

    def __init__(self, device_name: str, execution_id: str, log_id: str):
        self.device_name = device_name
        self.execution_id = execution_id
        self.log_id = log_id
        self.asdb_available = False
        self.ctx = None

        self._initialize()

    def _initialize(self):
        """Initialize with ASDB if available."""
        try:
            client = ASDBClient.from_env()
            self.ctx = ExecutionContext(
                client=client,
                device_name=self.device_name,
                execution_id=self.execution_id,
                execution_log_id=self.log_id,
                execution_type="production"
            )
            self.asdb_available = True
            log.info("ASDB integration active")
        except ASDBError as e:
            log.warning(f"ASDB unavailable: {e}")
            log.info("Continuing with local logging only")
            self.asdb_available = False

    def start(self):
        """Start execution (with or without ASDB)."""
        if self.asdb_available and self.ctx:
            try:
                self.ctx.start()
            except ASDBError as e:
                log.warning(f"Failed to update ASDB status: {e}")
        else:
            log.info(f"[LOCAL] Starting execution for {self.device_name}")

    def log_message(self, message: str, level: str = "info"):
        """Log message (with or without ASDB)."""
        if self.asdb_available and self.ctx:
            try:
                self.ctx.log(message, level)
            except ASDBError as e:
                log.warning(f"Failed to log to ASDB: {e}")
                # Still log locally
                getattr(log, level)(message)
        else:
            getattr(log, level)(f"[LOCAL] {message}")

    def complete(self, message: str, metadata: dict):
        """Complete execution (with or without ASDB)."""
        if self.asdb_available and self.ctx:
            try:
                self.ctx.complete(message, metadata)
            except ASDBError as e:
                log.warning(f"Failed to update ASDB: {e}")
                log.info(f"[LOCAL] Completed: {message}")
        else:
            log.info(f"[LOCAL] Completed: {message}")

def resilient_upgrade():
    """Upgrade that works with or without ASDB."""
    executor = ResilientExecutor(
        device_name="router-01.prod",
        execution_id="exec-123",
        log_id="log-456"
    )

    executor.start()
    executor.log_message("Starting upgrade process", "info")

    # Your upgrade logic here
    executor.log_message("Uploading image...", "info")
    # ...

    executor.complete("Upgrade successful", {})
    log.info("✓ Upgrade completed (check logs for ASDB status)")

if __name__ == "__main__":
    resilient_upgrade()
```

---

## 🧪 Testing Examples

### Example 10: Unit Tests with Mocks

```python
"""
test_upgrade.py - Unit tests using mocks
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from swimlib.asdb import ExecutionContext, ASDBError

class TestExecutionContext:
    """Test ExecutionContext behavior."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock ASDB client."""
        client = Mock()
        client.update_execution_log_status = Mock()
        client.append_log = Mock()
        client.create_device_history = Mock()
        return client

    @pytest.fixture
    def context(self, mock_client):
        """Create a test execution context."""
        return ExecutionContext(
            client=mock_client,
            device_name="test-device",
            execution_id="test-exec",
            execution_log_id="test-log",
            execution_type="production"
        )

    def test_start_updates_status(self, context, mock_client):
        """Test that start() updates execution status."""
        context.start()

        mock_client.update_execution_log_status.assert_called_once_with(
            "test-log",
            "in_progress"
        )

    def test_log_sends_to_asdb(self, context, mock_client):
        """Test that log() sends messages to ASDB."""
        context.start()
        context.log("Test message", "info")

        mock_client.append_log.assert_called_with(
            "test-log",
            "Test message",
            "info"
        )

    def test_complete_creates_history(self, context, mock_client):
        """Test that complete() creates device history."""
        context.start()
        metadata = {"version": "18.1.0"}
        context.complete("Success", metadata)

        # Verify history creation
        mock_client.create_device_history.assert_called_once()
        call_args = mock_client.create_device_history.call_args
        assert call_args[1]["metadata"] == metadata

    def test_dry_run_skips_history(self, mock_client):
        """Test that dry_run execution skips history creation."""
        ctx = ExecutionContext(
            client=mock_client,
            device_name="test-device",
            execution_id="test-exec",
            execution_log_id="test-log",
            execution_type="dry_run"
        )

        ctx.start()
        ctx.complete("Success", {})

        # History should not be created for dry_run
        mock_client.create_device_history.assert_not_called()

    def test_fail_raises_error(self, context):
        """Test that fail() raises ASDBError."""
        context.start()

        with pytest.raises(ASDBError):
            context.fail("Test failure", {})

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Example 11: Integration Tests

```python
"""
test_integration.py - Integration tests with real ASDB
Requires: Valid ASDB credentials in environment
"""

import pytest
import os
from swimlib.asdb import ASDBClient, ExecutionContext, ASDBError

@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("ASDB_BASE_URL"),
    reason="ASDB credentials not configured"
)
class TestASDBIntegration:
    """Integration tests requiring real ASDB connection."""

    @pytest.fixture
    def client(self):
        """Create real ASDB client."""
        return ASDBClient.from_env()

    def test_client_initialization(self, client):
        """Test that client initializes with valid credentials."""
        assert client is not None
        assert client.mode == os.getenv("ASDB_MODE", "remote")

    def test_full_execution_lifecycle(self, client):
        """Test complete execution lifecycle with real ASDB."""
        ctx = ExecutionContext(
            client=client,
            device_name="integration-test-device",
            execution_id="test-exec-001",
            execution_log_id="test-log-001",
            execution_type="dry_run"  # Use dry_run for testing
        )

        # Should not raise
        ctx.start()
        ctx.log("Integration test message", "info")
        ctx.complete("Integration test complete", {})

@pytest.mark.unit
class TestLocalMode:
    """Tests using local mode (no real ASDB connection needed)."""

    @pytest.fixture(autouse=True)
    def setup_local_mode(self):
        """Force local mode for these tests."""
        original = os.environ.get("ASDB_MODE")
        os.environ["ASDB_MODE"] = "local"
        yield
        if original:
            os.environ["ASDB_MODE"] = original
        else:
            os.environ.pop("ASDB_MODE", None)

    def test_local_mode_no_errors(self):
        """Test that local mode operations don't raise errors."""
        client = ASDBClient.from_env()
        ctx = ExecutionContext(
            client=client,
            device_name="local-test",
            execution_id="local-exec",
            execution_log_id="local-log",
            execution_type="dry_run"
        )

        # None of these should raise in local mode
        ctx.start()
        ctx.log("Local test", "info")
        ctx.complete("Done", {})

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])
```

---

## 🌍 Real-World Scenarios

### Example 12: F5 BIG-IP Upgrade Workflow

```python
"""
f5_upgrade.py - Complete F5 BIG-IP upgrade workflow
"""

import hashlib
import paramiko
from pathlib import Path
from swimlib.asdb import (
    ASDBClient,
    ExecutionContext,
    build_upgrade_metadata,
    ASDBError
)
from swimlib import log

class F5Upgrader:
    """Handles F5 BIG-IP device upgrades."""

    def __init__(self, ctx: ExecutionContext, device_config: dict):
        self.ctx = ctx
        self.config = device_config
        self.ssh_client = None

    def connect(self):
        """Establish SSH connection to device."""
        self.ctx.log(f"Connecting to {self.config['host']}", "info")

        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.ssh_client.connect(
            hostname=self.config["host"],
            username=self.config["username"],
            password=self.config["password"],
            timeout=30
        )

        self.ctx.log("✓ SSH connection established", "info")

    def calculate_md5(self, file_path: str) -> str:
        """Calculate MD5 checksum of local file."""
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    def upload_image(self, local_path: str, remote_path: str) -> tuple:
        """Upload image via SFTP."""
        self.ctx.log(f"Uploading {local_path}...", "info")

        # Calculate local MD5
        local_md5 = self.calculate_md5(local_path)
        self.ctx.log(f"Local MD5: {local_md5}", "debug")

        # Upload via SFTP
        sftp = self.ssh_client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()

        # Verify remote MD5
        stdin, stdout, stderr = self.ssh_client.exec_command(
            f"md5sum {remote_path}"
        )
        remote_md5 = stdout.read().decode().split()[0]

        if local_md5 != remote_md5:
            raise ValueError("MD5 checksum mismatch!")

        self.ctx.log("✓ Upload verified", "info")
        return local_md5, remote_md5

    def install_image(self, image_path: str, volume: str):
        """Install image to specified volume."""
        self.ctx.log(f"Installing to volume {volume}...", "info")

        cmd = f"tmsh install sys software image {image_path} volume {volume}"
        stdin, stdout, stderr = self.ssh_client.exec_command(cmd, timeout=600)

        # Monitor installation
        for line in stdout:
            self.ctx.log(line.strip(), "debug")

        self.ctx.log("✓ Installation complete", "info")

    def upgrade(self):
        """Execute complete upgrade workflow."""
        try:
            self.connect()

            # Upload image
            local_md5, remote_md5 = self.upload_image(
                self.config["local_image"],
                self.config["remote_image"]
            )

            # Install
            self.install_image(
                self.config["remote_image"],
                self.config["target_volume"]
            )

            # Build metadata
            metadata = build_upgrade_metadata(
                target_version=self.config["target_version"],
                local_folder=str(Path(self.config["local_image"]).parent),
                remote_folder=str(Path(self.config["remote_image"]).parent),
                image_name=Path(self.config["local_image"]).name,
                md5_local=local_md5,
                md5_remote=remote_md5,
                current_version=self.config.get("current_version", "17.X"),
            )

            return metadata

        finally:
            if self.ssh_client:
                self.ssh_client.close()

def main():
    """Main upgrade entry point."""
    # Configuration (would typically come from args/config file)
    device_config = {
        "host": "bigip-01.company.com",
        "username": "admin",
        "password": "password",  # Use secure credential management!
        "local_image": "/opt/images/BIGIP-18.1.0-0.0.123.iso",
        "remote_image": "/shared/images/BIGIP-18.1.0-0.0.123.iso",
        "target_version": "18.1.0",
        "target_volume": "HD1.2",
    }

    try:
        client = ASDBClient.from_env()
        ctx = ExecutionContext(
            client=client,
            device_name=device_config["host"],
            execution_id="f5-upgrade-001",
            execution_log_id="log-001",
            execution_type="production"
        )

        ctx.start()

        upgrader = F5Upgrader(ctx, device_config)
        metadata = upgrader.upgrade()

        ctx.complete("F5 upgrade completed successfully", metadata)
        log.info("✓ Upgrade successful")

    except ASDBError as e:
        log.error(f"ASDB error: {e}")
        sys.exit(1)
    except Exception as e:
        log.error(f"Upgrade failed: {e}")
        try:
            ctx.fail(f"Upgrade failed: {e}", {})
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Example 13: Batch Processing with Queue

```python
"""
batch_processor.py - Process multiple upgrade tasks from a queue
"""

import json
from queue import Queue
from threading import Thread
from typing import Dict, List
from swimlib.asdb import ASDBClient, ExecutionContext, ASDBError
from swimlib import log

class UpgradeTask:
    """Represents a single upgrade task."""

    def __init__(self, task_data: dict):
        self.device_name = task_data["device_name"]
        self.execution_id = task_data["execution_id"]
        self.log_id = task_data["log_id"]
        self.config = task_data.get("config", {})

class BatchProcessor:
    """Process upgrade tasks from a queue."""

    def __init__(self, num_workers: int = 3):
        self.queue = Queue()
        self.num_workers = num_workers
        self.results = []

    def worker(self):
        """Worker thread to process tasks."""
        while True:
            task = self.queue.get()
            if task is None:
                break

            try:
                result = self.process_task(task)
                self.results.append(result)
            except Exception as e:
                log.error(f"Task failed for {task.device_name}: {e}")
                self.results.append({
                    "device": task.device_name,
                    "success": False,
                    "error": str(e)
                })
            finally:
                self.queue.task_done()

    def process_task(self, task: UpgradeTask) -> dict:
        """Process a single upgrade task."""
        log.info(f"Processing {task.device_name}...")

        try:
            client = ASDBClient.from_env()
            ctx = ExecutionContext(
                client=client,
                device_name=task.device_name,
                execution_id=task.execution_id,
                execution_log_id=task.log_id,
                execution_type="production"
            )

            ctx.start()
            ctx.log("Starting batch upgrade", "info")

            # Perform upgrade
            # ... upgrade logic ...

            ctx.complete("Batch upgrade complete", {})

            return {
                "device": task.device_name,
                "success": True,
                "message": "Upgrade completed"
            }

        except ASDBError as e:
            return {
                "device": task.device_name,
                "success": False,
                "error": str(e)
            }

    def run(self, tasks: List[Dict]):
        """Process all tasks using worker threads."""
        # Start workers
        threads = []
        for _ in range(self.num_workers):
            t = Thread(target=self.worker)
            t.start()
            threads.append(t)

        # Enqueue tasks
        for task_data in tasks:
            task = UpgradeTask(task_data)
            self.queue.put(task)

        # Wait for completion
        self.queue.join()

        # Stop workers
        for _ in range(self.num_workers):
            self.queue.put(None)
        for t in threads:
            t.join()

        return self.results

def main():
    """Load tasks from JSON and process."""
    # Load tasks from file
    with open("upgrade_tasks.json") as f:
        tasks = json.load(f)

    # Example tasks structure:
    # [
    #     {
    #         "device_name": "router-01",
    #         "execution_id": "exec-001",
    #         "log_id": "log-001",
    #         "config": {...}
    #     },
    #     ...
    # ]

    processor = BatchProcessor(num_workers=3)
    results = processor.run(tasks)

    # Print summary
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful

    log.info(f"\nBatch Processing Summary:")
    log.info(f"  Total: {len(results)}")
    log.info(f"  Successful: {successful}")
    log.info(f"  Failed: {failed}")

    # Save results
    with open("upgrade_results.json", "w") as f:
        json.dump(results, f, indent=2)

    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
```

---

## 📚 Additional Resources

- [Guides](GUIDES.md) - Comprehensive development guides
- [README.md](README.md) - Quick start and overview
- [CLAUDE.md](CLAUDE.md) - Architecture details

---

> [!TIP]
> For more complex use cases, combine patterns from multiple examples above.

---

<div align="center">

**Need help?** Check [GUIDES.md](GUIDES.md) for detailed documentation

</div>
