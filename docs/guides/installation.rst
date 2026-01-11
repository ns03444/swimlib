Installation Guide
==================

This guide covers installation of swimlib and its dependencies for different use cases.

Requirements
------------

**Python Version**

swimlib requires Python 3.13 or higher.

.. code-block:: bash

   # Check Python version
   python --version
   # Should output: Python 3.13.0 or higher

**System Dependencies**

- Poetry (for development)
- SSH client (for F5 device connections)
- Git (for source installation)

Installing swimlib
------------------

Using Poetry (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~

Poetry provides dependency management and virtual environment handling:

.. code-block:: bash

   # Add swimlib to your project
   poetry add swimlib

   # Or install in editable mode for development
   git clone https://github.com/nickspell/swimlib.git
   cd swimlib
   poetry install

Using pip
~~~~~~~~~

Install from PyPI:

.. code-block:: bash

   pip install swimlib

Or install from source:

.. code-block:: bash

   git clone https://github.com/nickspell/swimlib.git
   cd swimlib
   pip install -e .

Development Installation
------------------------

For contributing to swimlib or running tests:

.. code-block:: bash

   # Clone repository
   git clone https://github.com/nickspell/swimlib.git
   cd swimlib

   # Install with development dependencies
   poetry install

   # Activate virtual environment
   poetry shell

Dependencies
------------

Runtime Dependencies
~~~~~~~~~~~~~~~~~~~~

- **paramiko** - SSH/SFTP operations for device connections
- **requests** - HTTP client for ASDB API communication
- **rich** - Terminal formatting for enhanced logging

Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~

- **pytest** - Testing framework
- **black** - Code formatting
- **ruff** - Linting
- **mypy** - Type checking
- **sphinx** - Documentation generation
- **furo** - Modern documentation theme

Verification
------------

Verify installation:

.. code-block:: python

   # Test import
   import swimlib
   from swimlib import log
   from swimlib.asdb import ASDBClient

   # Check version
   print(f"swimlib installed successfully")
   log.info("Logging configured correctly")

Next Steps
----------

After installation, proceed to:

- :doc:`quickstart` - Basic usage examples
- :doc:`configuration` - Environment setup
- :doc:`workflows` - Common workflow patterns
