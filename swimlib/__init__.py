"""swimlib - Production-Grade Python SDK for ASDB API.

This module provides the core logging configuration for the swimlib package.
The logger is configured with Rich terminal formatting for enhanced output readability.

The module exports a singleton logger instance that can be imported and used throughout
the SDK and by client applications.

Module Attributes:
    log (logging.Logger): Configured logger instance with RichHandler for colored terminal output.
        The log level is controlled via the ``SWIMLIB_LOG_LEVEL`` environment variable.

Environment Variables:
    SWIMLIB_LOG_LEVEL (str): Sets the logging level. Valid values are DEBUG, INFO, WARNING, ERROR.
        Defaults to INFO if not set or if an invalid value is provided.

Example:
    Basic usage of the logger::

        from swimlib import log

        log.info("Starting device upgrade workflow")
        log.debug("Device configuration: %s", device_config)
        log.error("Failed to connect to device: %s", error_message)

Note:
    The logger is configured only once to prevent duplicate handlers. Subsequent imports
    will reuse the same configured logger instance.

See Also:
    - :mod:`rich.logging.RichHandler` for terminal formatting details
    - :mod:`swimlib.asdb` for ASDB client implementation

.. versionadded:: 0.1.0
"""
import os
import logging
from rich.logging import RichHandler

# module-level logger exposed as `from swimlib import log`
logger = logging.getLogger("swimlib")

# configure only once
if not logger.handlers:
    level_name = os.getenv("SWIMLIB_LOG_LEVEL", "INFO").upper()
    try:
        level = getattr(logging, level_name)
    except Exception:
        level = logging.INFO
    handler = RichHandler()
    handler.setLevel(level)
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False

log = logger

__all__ = ["log"]