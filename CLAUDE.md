# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`swimlib` is a production-grade Python SDK for the ASDB (Automated Software Database) API. It provides clean abstractions for managing device executions, logging, and status tracking in network automation workflows, with a focus on F5 BIGIP device upgrades.

**Key principle**: This is a library SDK that raises exceptions (`ASDBError`) rather than calling `sys.exit()`. CLI applications should catch exceptions and handle process termination.

## Architecture

### Core Components

1. **ASDBClient** ([swimlib/asdb.py](swimlib/asdb.py:14-174))
   - Low-level HTTP client for ASDB API operations
   - Supports two modes:
     - `remote`: Makes actual API calls (production)
     - `local`: Logs requests without HTTP calls (testing/dry-run)
   - Initialize via `ASDBClient.from_env()` to read from environment variables
   - All methods raise `ASDBError` on failure - never terminates the process
   - Validates required configuration (base_url, api_token) on initialization
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

3. **Logging** ([swimlib/__init__.py](swimlib/__init__.py))
   - Module-level logger configured with RichHandler for terminal output
   - Import as: `from swimlib import log`
   - Control verbosity via `SWIMLIB_LOG_LEVEL` env var (default: INFO)

### Design Patterns

- **Exception-based error handling**: All errors raise `ASDBError`. CLI callers decide whether to exit
- **Graceful degradation**: ASDB API failures are logged but don't break local execution
- **Mode switching**: Use `local` mode for testing workflows without making real API calls
- **Execution types**: `production` creates history records, `dry_run` skips them
- **No Device dataclass**: Removed in refactor - parameters are passed explicitly to avoid unnecessary abstraction

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

## Development Commands

This project uses Poetry for dependency management:

```bash
# Install dependencies
poetry install

# Build package
poetry build

# Run Python with swimlib in path
poetry run python -m swimlib.main
```

## Environment Variables

Required for ASDB client operation:
- `ASDB_BASE_URL` - Base URL for ASDB API (e.g., `https://asdb.example.com`)
- `ASDB_TOKEN` - API authentication token
- `ASDB_MODE` - Operation mode: `remote` (default) or `local`
- `SWIMLIB_LOG_LEVEL` - Logging level: `DEBUG`, `INFO` (default), `WARNING`, `ERROR`

## Metadata Structure

Device upgrade history uses standardized metadata via `build_upgrade_metadata()` ([swimlib/asdb.py](swimlib/asdb.py:301-337)):
- BIGIP-specific fields: image name, versions, volumes
- Upload/checksum status tracking
- Source/destination paths for file operations
- Change request references (CR numbers)
- Configurable current version (defaults to "17.X")
- All parameters are explicit - no Device dataclass required
