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