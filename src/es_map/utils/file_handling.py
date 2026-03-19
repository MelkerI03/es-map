import os
from pathlib import Path
import shutil

from es_map.utils.logging import get_logger

logger = get_logger(__name__)


def overwrite_copy(src: Path, dst: Path) -> None:
    try:
        if dst.exists():
            os.remove(dst)
        shutil.copy(src, dst)
    except PermissionError:
        print(f"File locked: {dst}, skipping...")
