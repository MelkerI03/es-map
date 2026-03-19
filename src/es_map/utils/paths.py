from functools import lru_cache
import sys
from pathlib import Path

from es_map.utils.definitions import ROOT_DIR


@lru_cache(maxsize=1)  # Cache for 'single' lookup
def get_root_path() -> Path:
    """
    Get a path the project root
    """
    if hasattr(sys, "_MEIPASS"):
        path = Path(sys._MEIPASS)  # pyright: ignore[reportAttributeAccessIssue]
        # path = ROOT_DIR
    else:
        path = ROOT_DIR

    return path
