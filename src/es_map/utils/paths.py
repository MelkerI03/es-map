"""Path utilities for resolving project-level filesystem locations.

This module provides helpers for determining the root directory of the
project, with support for both standard execution and bundled
(enhanced) environments such as PyInstaller.
"""

import sys
from functools import lru_cache
from pathlib import Path

from es_map.utils.logging import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)  # Cache for 'single' lookup
def get_root_path() -> Path:
    """Get the root path of the project.

    Handles both:
        - Standard Python execution
        - Bundled environments (e.g. PyInstaller)

    Returns:
        Path: Absolute path to the project root directory.
    """
    if hasattr(sys, "_MEIPASS"):
        root_path = Path(sys._MEIPASS)  # pyright: ignore[reportAttributeAccessIssue]
    else:
        root_path = Path(__file__).parents[1]  # ./..

    logger.debug(
        "Resolved project root path",
        extra={"root_path": str(root_path)},
    )

    return root_path
