swimlib Documentation
=====================

.. image:: https://img.shields.io/badge/python-3.13+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code Style: Black

**swimlib** is a production-grade Python SDK for the ASDB (Automated Software Database) API,
providing clean abstractions for managing device executions, logging, and status tracking in
network automation workflows, with a focus on F5 BIG-IP device upgrades.


Installation
~~~~~~~~~~~~
Using Poetry (recommended):

.. code-block:: bash

   poetry add swimlib

Or with pip:

.. code-block:: bash

   pip install swimlib

Basic Usage
~~~~~~~~~~~

Initialize the ASDB client and execute a device upgrade workflow:

.. code-block:: python

   from swimlib.asdb import ASDBClient
   from swimlib import log

   # Initialize client from environment variables
   client = ASDBClient(
       device={
           "execution_log_id": "log-123",
           "device_name": "router-01",
           "execution_type": "production"
       }
   )

   # Log and track progress
   client.send_log("Starting device upgrade", log_level="info")
   log.info("Upgrade workflow initiated")

   # Complete execution
   client.pass_device_execution("Upgrade completed successfully")

Environment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

Set required environment variables:

.. code-block:: bash

   export ASDB_BASE_URL="https://asdb.example.com"
   export ASDB_TOKEN="your-api-token"
   export ASDB_MODE="remote"  # or "local" for testing
   export SWIMLIB_LOG_LEVEL="INFO"

Architecture Overview
---------------------

swimlib follows a modular architecture with three core components:

.. code-block:: text

   ┌─────────────────┐
   │ CLI Application │
   └────────┬────────┘
            │
            ├──────────────────┐
            │                  │
            ▼                  ▼
   ┌──────────────┐   ┌───────────────┐
   │ ASDBClient   │   │ SSHConnection │
   └──────┬───────┘   └───────┬───────┘
          │                   │
          ▼                   ▼
   ┌─────────────┐    ┌──────────────┐
   │  ASDB API   │    │  F5 Device   │
   │             │    │              │
   │ • Logs      │    │ • Commands   │
   │ • Status    │    │ • SFTP       │
   │ • History   │    │              │
   └─────────────┘    └──────────────┘

Core Modules
~~~~~~~~~~~~

:mod:`swimlib.asdb`
   ASDB API client for execution management

:mod:`swimlib.ssh_connect`
   SSH connection manager with context support

:mod:`swimlib.software_matrix`
   F5 software configuration matrix

:mod:`swimlib.f5`
   F5 BIG-IP upgrade workflows

Design Principles
~~~~~~~~~~~~~~~~~

**Exception-Based Error Handling**
   The library raises exceptions instead of calling ``sys.exit()``, allowing
   CLI applications to decide how to handle failures.

**Graceful Degradation**
   ASDB API failures are logged but don't break local execution flow.

**Mode Switching**
   ``remote`` mode for production API calls, ``local`` mode for testing without
   network requests.

**Execution Types**
   ``production`` creates permanent history records, ``dry_run`` validates
   without persisting changes.

Documentation Sections
----------------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   guides/installation
   guides/quickstart
   guides/configuration
   guides/workflows
   guides/testing
   guides/best_practices

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/basic_usage
   examples/f5_upgrade
   examples/error_handling
   examples/parallel_execution
   examples/testing_strategies

.. toctree::
   :maxdepth: 3
   :caption: API Reference

   api/core
   api/f5
   api/ssh
   api/exceptions

.. toctree::
   :maxdepth: 1
   :caption: Development

   development/contributing
   development/changelog
   development/roadmap

Supported Platforms
-------------------

F5 BIG-IP
~~~~~~~~~

* ✅ Virtual Edition (VE) - Target: 21.0.0
* ✅ vCMP Guests - Target: 21.0.0
* ✅ Hardware iSeries (i2800, i5800, i7800, i10800, i15800) - Target: 17.5.1.3
* ✅ Legacy platforms (5250, 7200) - Target: 17.5.1.3
* ✅ rSeries Tenants - Target: 21.0.0

Other Vendors
~~~~~~~~~~~~~

* 🚧 Citrix NetScaler (in development)
* 🚧 Palo Alto Networks (in development)

Workflow Phases
---------------

F5 BIG-IP upgrades follow a four-phase workflow:

1. **Pre-Validation** (``dry_run``)
   - Software lookup and validation
   - SSH connectivity testing
   - Remote storage validation

2. **Image Copy** (``image_copy``)
   - SFTP transfer with MD5 validation
   - Intelligent skip logic for existing files

3. **Image Stage** (``image_stage``)
   - Software installation to inactive volume
   - Version verification
   - No device reboot

4. **Image Upgrade** (``image_upgrade``)
   - Reboot to upgraded volume
   - Service interruption expected

Community & Support
-------------------

.. important::

   This is a production library. Please report issues on GitHub and follow
   security best practices when handling credentials and API tokens.

**Links**

* 📚 Full Documentation: https://swimlib.readthedocs.io
* 🐛 Issue Tracker: https://github.com/nickspell/swimlib/issues
* 💬 Discussions: https://github.com/nickspell/swimlib/discussions

**Contributing**

Contributions are welcome! Please see :doc:`development/contributing` for guidelines.

License
-------

This project is licensed under the terms described in the LICENSE file.


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
