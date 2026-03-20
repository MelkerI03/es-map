"""
File handling utilities for safe and consistent filesystem operations.

This module provides helper functions for copying and managing files.
"""

import shutil
from pathlib import Path

from es_map.utils.logging import get_logger

logger = get_logger(__name__)


def overwrite_copy(src: Path, dst: Path) -> None:
    """
    Copy a file to a destination, overwriting it if it already exists.

    If the destination file is locked or cannot be removed, the operation
    is skipped.

    Args:
        src: Source file path.
        dst: Destination file path.

    Raises:
        OSError: If copying fails for reasons other than permission issues.
    """
    try:
        if dst.exists():
            logger.debug("Overwriting existing file", extra={"dst": str(dst)})
            dst.unlink()

        shutil.copy(src, dst)

        logger.debug(
            "Copied file",
            extra={"src": str(src), "dst": str(dst)},
        )
    except PermissionError:
        logger.warning(
            "File locked, skipping copy",
            extra={"destination": str(dst)},
        )
