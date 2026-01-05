# swimlib

Production-grade Python SDK for automating F5 BIG-IP device upgrades via ASDB API.

## Features

- **Image Copy**: SFTP transfer with MD5 validation
- **Image Stage**: Install software to inactive volume
- **Image Upgrade**: Reboot to upgraded volume
- **ASDB Integration**: Execution tracking, logging, and status updates

## Quick Start

```bash
poetry install
poetry build
```

## Environment Variables

```bash
ASDB_BASE_URL=https://asdb.example.com
ASDB_TOKEN=your_token
ASDB_MODE=remote              # or 'local' for dry-run
SWIMLIB_LOG_LEVEL=INFO
```

## Usage

```python
from swimlib.asdb import ASDBClient, ExecutionContext

client = ASDBClient.from_env()
ctx = ExecutionContext(
    client=client,
    device_name="router-01",
    execution_id="exec-123",
    execution_log_id="log-456",
    execution_type="production"
)

ctx.start()
ctx.log("Starting upgrade...")
# ... perform upgrade operations ...
ctx.complete("Upgrade complete", metadata)
```

## Workflow Modes

- `dry_run`: Pre-validation only
- `image_copy`: Copy artifacts to device
- `image_stage`: Copy + install to inactive volume
- `image_upgrade`: Copy + install + reboot

## Architecture

Library raises `ASDBError` exceptions - never calls `sys.exit()`. CLI applications handle process termination.

See [CLAUDE.md](CLAUDE.md) for detailed architecture and development guidance.
