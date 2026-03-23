"""File handling utilities for safe and consistent filesystem operations.

This module provides helper functions for copying and managing files.
"""

import shutil
from pathlib import Path

from es_map.utils.logging import get_logger

logger = get_logger(__name__)


def prepare_output_dir(output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)


def copy_and_replace(src: Path, dst: Path) -> None:
    """
    Copy a file or directory to a destination, overwriting existing content.

    - If src is a file → copied as a file
    - If src is a directory → copied recursively
    - Existing files/directories at destination are overwritten
    """

    if not src.exists():
        raise FileNotFoundError(f"Source does not exist: {src}")

    # --- CASE 1: Source is a file ---
    if src.is_file():
        if dst.exists() and dst.is_dir():
            dst = dst / src.name

        dst.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(src, dst)
        return

    # --- CASE 2: Source is a directory ---
    if src.is_dir():
        if dst.exists() and dst.is_file():
            raise ValueError("Cannot copy directory into a file")

        # Ensure destination directory exists
        dst.mkdir(parents=True, exist_ok=True)

        for item in src.iterdir():
            target = dst / item.name

            if item.is_dir():
                # Recursively copy directory
                copy_and_replace(item, target)
            else:
                if target.exists():
                    target.unlink()
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)

        return

    raise ValueError(f"Unsupported source type: {src}")
