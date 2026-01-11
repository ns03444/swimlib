# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`swimlib` is a production-grade Python SDK for the ASDB (Automated Software Database) API. It provides clean abstractions for managing device executions, logging, and status tracking in network automation workflows, with a focus on F5 BIG-IP device upgrades.

**Key principle**: This is a library SDK that raises exceptions (`ASDBError`) rather than calling `sys.exit()`. CLI applications should catch exceptions and handle process termination.

## Development Commands

```bash
# Install dependencies (includes dev and docs groups)
poetry install

# Install with specific dependency groups
poetry install --with dev
poetry install --with docs

# Build package
poetry build

# Run tests with coverage
poetry run pytest
poetry run pytest -v --cov=swimlib --cov-report=term-missing

# Code quality checks
poetry run black swimlib/              # Format code (line length: 100)
poetry run ruff swimlib/               # Lint code
poetry run mypy swimlib/               # Type checking

# Build documentation (Sphinx)
poetry run sphinx-build -b html docs public

# Run module directly
poetry run python -m swimlib.main
```

## Architecture

### Core Components

1. **ASDBClient** ([swimlib/asdb.py](swimlib/asdb.py:14-174))
   - Low-level HTTP client for ASDB API operations
   - Supports two modes:
     - `remote`: Makes actual API calls (production)
     - `local`: Logs requests without HTTP calls (testing/dry-run)
   - Initialize via `ASDBClient.from_env()` to read from environment variables
   - All methods raise `ASDBError` on failure - never terminates the process
   - Core methods:
     - `update_execution_log_status(execution_log_id, status)` - Update execution status
     - `append_log(execution_log_id, message, log_level)` - Send log entries to ASDB
     - `update_device_status(device_name, conn_status)` - Update device connection status
     - `create_device_history(execution_id, device_name, stage, metadata)` - Create history records

2. **ExecutionContext** ([swimlib/asdb.py](swimlib/asdb.py:177-298))
   - High-level orchestrator for execution lifecycle management
   - Handles the common pattern: `start()` → `log()` → `complete()` or `fail()`
   - Manages status updates, logging (local + remote), and history tracking
   - Automatically skips history creation for dry-run executions
   - **Use this in CLI scripts** rather than calling ASDBClient directly
   - Methods:
     - `start()` - Mark execution as in-progress (raises ASDBError on failure)
     - `log(message, level)` - Log locally and to ASDB (gracefully handles ASDB failures)
     - `complete(message, metadata)` - Successful completion with history (raises ASDBError on failure)
     - `fail(message, metadata)` - Mark as failed and raise ASDBError (always raises)

3. **SSHConnection** ([swimlib/ssh_connect.py](swimlib/ssh_connect.py:97-227))
   - Context manager for paramiko SSH connections with automatic cleanup
   - Disables key-based auth (password-only) and host key verification (AutoAddPolicy)
   - Raises `SSHAuthError` for authentication failures
   - Example usage:
     ```python
     with SSHConnection(ip, username, password) as ssh:
         stdin, stdout, stderr = ssh.exec_command("tmsh show sys version")
     ```

4. **Software Matrix** ([swimlib/software_matrix.py](swimlib/software_matrix.py))
   - Configuration mapping of F5 BIG-IP device models to software artifacts
   - Maps device models → target versions, paths, MD5 checksums, download URLs
   - Supports VE, vCMP, iSeries (i2800-i15800), legacy (5250, 7200), rSeries platforms
   - Accessed via `software_matrix` dictionary (key: device model name)

5. **F5 Upgrade Workflow** ([swimlib/f5/run.py](swimlib/f5/run.py))
   - Main orchestration logic for F5 BIG-IP upgrade workflows
   - Execution types determine workflow scope:
     - `dry_run`: Pre-validation only (SSH, storage, software lookup)
     - `image_copy`: Pre-validation + SFTP transfer with MD5 validation
     - `image_stage`: image_copy + install to inactive volume (no reboot)
     - `image_upgrade`: image_stage + reboot to upgraded volume
   - Reads configuration from `SWIMLIB_DEVICE_JSON` environment variable

6. **F5 Actions** (swimlib/f5/actions/)
   - `image_copy.py`: SFTP artifact transfer with MD5 checksum validation, skip logic for existing files
   - `image_stage.py`: Install software to inactive volume using `tmsh` commands
   - `image_upgrade.py`: Reboot device to target volume

### Design Patterns

- **Exception-based error handling**: All errors raise `ASDBError`. CLI callers decide whether to exit
- **Graceful degradation**: ASDB API failures are logged but don't break local execution
- **Mode switching**: Use `local` mode for testing workflows without making real API calls
- **Execution types**: `production` creates history records, `dry_run` skips them
- **Context managers**: SSHConnection auto-closes on exit, even with exceptions
- **Intelligent transfers**: SFTP copy skips files with valid checksums already on remote device

### Typical Usage Pattern

```python
from swimlib.asdb import ASDBClient, ExecutionContext, build_upgrade_metadata, ASDBError

try:
    # Initialize client from environment
    client = ASDBClient.from_env()

    # Create execution context
    ctx = ExecutionContext(
        client=client,
        device_name="router-01",
        execution_id="exec-123",
        execution_log_id="log-456",
        execution_type="production"
    )

    # Run workflow
    ctx.start()
    ctx.log("Starting device upgrade...")

    # ... do actual work ...

    metadata = build_upgrade_metadata(
        target_version="18.1.0",
        local_folder="/local/images",
        remote_folder="/var/images"
    )
    ctx.complete("Upgrade successful", metadata)

except ASDBError as e:
    # CLI handles exit
    print(f"Error: {e}")
    sys.exit(1)
```

## Environment Variables

Required for ASDB client operation:
- `ASDB_BASE_URL` - Base URL for ASDB API (e.g., `https://asdb.example.com`)
- `ASDB_TOKEN` - API authentication token
- `ASDB_MODE` - Operation mode: `remote` (default) or `local`
- `SWIMLIB_LOG_LEVEL` - Logging level: `DEBUG`, `INFO` (default), `WARNING`, `ERROR`

F5 workflow-specific:
- `SWIMLIB_DEVICE_JSON` - JSON string containing device configuration (model, execution_type, etc.)
- `SWIMLIB_SSH_USERNAME` - SSH username (default: "admin")
- `SWIMLIB_SSH_PASSWORD` - SSH password (default: "admin")

## Metadata Structure

Device upgrade history uses standardized metadata via `build_upgrade_metadata()` ([swimlib/asdb.py](swimlib/asdb.py:301-337)):
- BIGIP-specific fields: image name, versions, volumes
- Upload/checksum status tracking
- Source/destination paths for file operations
- Change request references (CR numbers)
- Configurable current version (defaults to "17.X")

## Documentation

- Built with Sphinx + Furo theme
- Deployed to GitLab Pages via `.gitlab-ci.yml`
- Uses Google-style docstrings with reStructuredText markup
- Extensions: copybutton, inline-tabs, myst-parser, napoleon

## Testing

- Test framework: pytest with pytest-cov
- Test paths: `tests/` directory
- Test pattern: `test_*.py` files, `Test*` classes, `test_*` functions
- Coverage reporting: Terminal output with missing lines highlighted
