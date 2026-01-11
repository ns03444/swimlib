# Design Proposals

## 1. Current Design

The current design aims for simplicity & clear organization by grouping similar processes together. It aims at keeping modules short, simple & self-contained for easy testing & resusability.

#### Top-Level Modules

These are modules that are shared across all platforms:

- `asdb.py`
- `software_matrix.py`
- `ssh_connect.py`

#### Platform Modules

Each platform has one lib of modules for:
1. pre validation
2. actions (image copy, stage and/or upgrade)
3. post validation

Each platform is compiled by `run.py` which runs each phase and sends logs to ASDB.

#### Package Structure

```bash
swimlib/
|____asdb.py
|____ssh_connect.py
|____software_matrix.py
|
|____f5/
| |____actions/
| | |____image_copy.py
| | |____image_stage.py
| | |____image_upgrade.py
| |____preval.py
| |____postval.py
| |____templates/
| |____run.py
|
|____netscaler/
| |____actions/
| | |____image_copy.py
| | |____image_upgrade.py
| |____preval.py
| |____postval.py
| |____run.py
|
|____paloalto/
| |____actions/
| |____preval.py
| |____postval.py
| |____run.py
```

**Strengths:** Simple, clear platform boundaries, easy to understand
**Trade-offs:** Code duplication across platforms, limited abstraction

---

## 2. Plugin-Based Design (Ansible/Nornir-Inspired)

Organizes code by **function type** rather than platform, using a plugin architecture. Plugins are dynamically loaded based on device platform, enabling extensibility and clean separation of concerns.

**Core Concepts:**
- **Actions**: Execute operations (copy, install, reboot)
- **Validators**: Pre/post-validation checks
- **Parsers**: Transform device output to structured data
- **Inventory**: Device metadata and grouping
- **Tasks**: Composable workflow units

#### Package Structure

```bash
swimlib/
|____core/
| |____plugin_loader.py       # Dynamic plugin discovery
| |____task_runner.py          # Task orchestration
| |____inventory.py            # Device inventory management
|
|____plugins/
| |____actions/
| | |____base.py               # Abstract base class
| | |____image_copy.py         # Platform-agnostic copy logic
| | |____image_install.py
| | |____reboot.py
| |
| |____validators/
| | |____base.py
| | |____storage_check.py      # Disk space validation
| | |____version_check.py      # Software version parsing
| | |____connectivity.py       # SSH/API reachability
| |
| |____parsers/
| | |____base.py
| | |____f5_parser.py          # TextFSM templates for F5
| | |____netscaler_parser.py
| | |____paloalto_parser.py
| |
| |____platforms/              # Platform-specific overrides
| | |____f5.py                 # F5-specific implementations
| | |____netscaler.py
| | |____paloalto.py
|
|____inventory/
| |____devices.yaml            # Device inventory
| |____groups.yaml             # Device groupings
|
|____workflows/
| |____upgrade.yaml            # Declarative workflow definition
| |____backup.yaml
```

**Example Workflow Definition** (YAML-driven):

```yaml
# workflows/upgrade.yaml
tasks:
  - name: validate_storage
    plugin: validators.storage_check
    params:
      min_space_gb: 5

  - name: copy_image
    plugin: actions.image_copy
    params:
      source: "{{ software_matrix[device.model].path }}"
      verify_checksum: true

  - name: install_image
    plugin: actions.image_install

  - name: validate_install
    plugin: validators.version_check
```

**Strengths:** Highly extensible, DRY principles, declarative workflows
**Trade-offs:** More abstraction layers, steeper learning curve

---

## 3. Stateful Multi-Vendor Design (Nornir + NAPALM + Netmiko)

Leverages **Nornir** for multi-threaded task execution, **NAPALM** for vendor-neutral abstractions, and **Netmiko** for low-level CLI access. Focus on stateful operations with rollback capabilities.

**Core Concepts:**
- **Nornir inventory**: Multi-source inventory (YAML, NetBox, ASDB)
- **NAPALM getters**: Standardized fact retrieval across vendors
- **Netmiko send_command**: Raw CLI for vendor-specific operations
- **Task functions**: Composable units executed per-device
- **Result objects**: Structured output with success/failure tracking

#### Package Structure

```bash
swimlib/
|____core/
| |____nornir_init.py          # Nornir initialization with ASDB inventory
| |____result_processor.py     # Parse Nornir results → ASDB logs
|
|____tasks/
| |____upgrade/
| | |____preval.py             # Nornir task: Pre-upgrade validation
| | |____transfer.py           # Nornir task: SCP/SFTP transfer
| | |____install.py            # Nornir task: Install software
| | |____postval.py            # Nornir task: Post-upgrade checks
| |
| |____backup/
| | |____config_backup.py      # NAPALM get_config()
| | |____state_snapshot.py     # NAPALM getters (facts, interfaces)
|
|____adapters/
| |____napalm_f5.py            # Custom NAPALM driver for F5
| |____napalm_netscaler.py     # NAPALM driver for Netscaler
|
|____inventory/
| |____asdb_inventory.py       # Nornir inventory plugin for ASDB API
| |____devices.yaml            # Fallback static inventory
|
|____templates/
| |____f5_install.j2           # Jinja2 template for tmsh commands
| |____netscaler_install.j2
|
|____workflows/
| |____upgrade_workflow.py     # Orchestrates Nornir task sequence
```

**Example Task Function**:

```python
# tasks/upgrade/preval.py
from nornir.core.task import Task, Result
from napalm import get_network_driver

def validate_upgrade_readiness(task: Task, min_space_gb: int) -> Result:
    """Nornir task: Validate device is ready for upgrade."""

    # Use NAPALM for standardized facts
    driver = get_network_driver(task.host.platform)
    device = driver(
        hostname=task.host.hostname,
        username=task.host.username,
        password=task.host.password
    )
    device.open()

    facts = device.get_facts()
    available_space = get_available_storage(device)  # Vendor-specific

    if available_space < min_space_gb:
        return Result(host=task.host, failed=True,
                     result=f"Insufficient storage: {available_space}GB")

    return Result(host=task.host, result={"facts": facts, "storage_gb": available_space})
```

**Strengths:** Battle-tested libraries, parallel execution, vendor abstraction
**Trade-offs:** NAPALM limited to common operations, requires custom drivers for full coverage

---

## 4. Test-Driven Validation Design (pyATS/Genie)

Uses **pyATS** and **Genie** for structured device interaction and state validation. Focuses on **test cases** as first-class citizens, with parsers for 3000+ CLI commands across vendors.

**Core Concepts:**
- **Testbed**: YAML-defined device topology
- **Genie parsers**: CLI output → structured Python dicts (TextFSM++, regex)
- **Genie models**: Vendor-neutral device state models
- **pyATS tests**: Unit/integration tests for device state
- **Diff snapshots**: Before/after state comparison

#### Package Structure

```bash
swimlib/
|____testbed/
| |____production.yaml         # pyATS testbed definition
| |____staging.yaml
|
|____jobs/
| |____upgrade_job.py          # pyATS job orchestrating test suite
|
|____tests/
| |____preval/
| | |____test_storage.py       # pyATS test: Storage check
| | |____test_version.py       # pyATS test: Current version
| | |____test_ha_sync.py       # pyATS test: HA cluster state
| |
| |____postval/
| | |____test_services.py      # pyATS test: Service health
| | |____test_routing.py       # pyATS test: Routing tables
|
|____triggers/
| |____image_copy.py           # pyATS trigger: Copy image
| |____image_install.py        # pyATS trigger: Install image
| |____reboot.py               # pyATS trigger: Reboot device
|
|____parsers/                  # Custom parsers (extends Genie)
| |____f5_cluster_status.py
| |____netscaler_lb_vserver.py
|
|____models/
| |____upgrade_state.py        # State model for upgrades
|
|____utils/
| |____asdb_reporter.py        # Convert pyATS results → ASDB logs
```

**Example Testbed**:

```yaml
# testbed/production.yaml
testbed:
  name: production_devices

devices:
  f5-ltm-01:
    os: bigip
    type: f5-ltm
    connections:
      ssh:
        protocol: ssh
        ip: 10.1.1.100
    credentials:
      default:
        username: "%ENV{SWIMLIB_SSH_USERNAME}"
        password: "%ENV{SWIMLIB_SSH_PASSWORD}"
```

**Example Test Case**:

```python
# tests/preval/test_storage.py
from pyats import aetest
from genie.utils.diff import Diff

class CheckStorage(aetest.Testcase):

    @aetest.test
    def verify_disk_space(self, device, min_space_gb=5):
        """Verify device has sufficient storage for upgrade."""

        # Genie parser auto-selects vendor-specific parser
        output = device.parse("show sys disk directory")

        available_gb = output['disk']['/shared']['available_gb']

        if available_gb < min_space_gb:
            self.failed(f"Insufficient space: {available_gb}GB < {min_space_gb}GB")
        else:
            self.passed(f"Storage OK: {available_gb}GB available")
```

**Strengths:** Rich parsers (3000+ commands), state diffing, Cisco-backed ecosystem
**Trade-offs:** Heavy dependency, verbose syntax, F5/Netscaler parsers may need custom development

---

## 5. Hybrid Modular Design (Current + Enhancements)

Enhances the current design with **best-of-breed** tools while preserving simplicity. Integrates Netmiko for transport, TextFSM for parsing, and optional Nornir for parallelism.

**Enhancements:**
- Replace raw Paramiko with **Netmiko** (ConnectHandler, exception handling)
- Add **TextFSM templates** for structured parsing (ntc-templates library)
- Optional **Nornir integration** for multi-device orchestration
- **Pydantic models** for configuration validation
- **Tenacity** for retry logic on transient failures

#### Package Structure

```bash
swimlib/
|____core/
| |____connection.py           # Netmiko wrapper with retry logic
| |____parser.py               # TextFSM template manager
| |____models.py               # Pydantic models for config validation
|
|____platforms/
| |____f5/
| | |____actions/
| | | |____image_copy.py       # Uses Netmiko file_transfer()
| | | |____image_stage.py
| | | |____image_upgrade.py
| | |____parsers/
| | | |____show_sys_version.textfsm
| | | |____show_sys_disk.textfsm
| | |____preval.py
| | |____postval.py
| | |____run.py
| |
| |____netscaler/
| | |____actions/
| | |____parsers/
| | |____run.py
|
|____shared/
| |____asdb.py
| |____software_matrix.py
| |____nornir_runner.py        # Optional: Nornir task wrapper
|
|____templates/                # Jinja2 command templates
| |____f5_install.j2
|
|____schemas/                  # Pydantic validation schemas
| |____device_config.py
| |____execution_config.py
```

**Example Netmiko Integration**:

```python
# core/connection.py
from netmiko import ConnectHandler
from tenacity import retry, stop_after_attempt, wait_exponential

class DeviceConnection:
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def connect(self, device_config):
        """Connect with automatic retry on transient failures."""
        return ConnectHandler(
            device_type='f5_linux',  # Netmiko device type
            host=device_config.ip,
            username=device_config.username,
            password=device_config.password,
            global_delay_factor=2
        )
```

**Example TextFSM Parser**:

```textfsm
# platforms/f5/parsers/show_sys_version.textfsm
Value VERSION (\S+)
Value BUILD (\S+)
Value PRODUCT (\S+)

Start
  ^Main Package.*Version\s+${VERSION}
  ^Main Package.*Build\s+${BUILD}
  ^Product\s+${PRODUCT} -> Record
```

**Strengths:** Minimal refactor, proven tools, maintains simplicity
**Trade-offs:** Less abstraction than plugin model, manual parser creation

---

## Comparison Matrix

| Design | Extensibility | Complexity | Multi-Device | Vendor Abstraction | Best For |
|--------|--------------|------------|--------------|-------------------|----------|
| Current (1) | Medium | Low | Manual | None | Single-device workflows, rapid prototyping |
| Plugin-Based (2) | High | Medium-High | Via custom code | Custom | Large teams, many platforms |
| Nornir+NAPALM (3) | High | Medium | Native (threaded) | High (limited ops) | Multi-device, common operations |
| pyATS/Genie (4) | Medium | High | Native | High (Cisco-focused) | Test-driven, state validation |
| Hybrid (5) | Medium | Low-Medium | Optional (Nornir) | Medium (TextFSM) | Evolutionary upgrade path |

---

## Recommendations

- **For immediate iteration**: **Design 5 (Hybrid)** - drop-in Netmiko/TextFSM upgrades with minimal disruption
- **For scale/parallelism**: **Design 3 (Nornir)** - native multi-threading, mature ecosystem
- **For extensibility**: **Design 2 (Plugin)** - future-proof architecture for diverse platforms
- **For validation-heavy workflows**: **Design 4 (pyATS)** - rich parsers, state diffing

---

## References

- [Nornir Documentation](https://nornir.readthedocs.io/)
- [NAPALM Documentation](https://napalm.readthedocs.io/)
- [Netmiko GitHub](https://github.com/ktbyers/netmiko)
- [pyATS/Genie Documentation](https://developer.cisco.com/docs/pyats/)
- [TextFSM Templates (ntc-templates)](https://github.com/networktocode/ntc-templates)
- [Ansible Network Automation](https://docs.ansible.com/ansible/latest/network/index.html)
- [DevNet Expert Training](https://docs.devnetexperttraining.com/)
