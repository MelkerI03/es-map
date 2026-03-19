from functools import lru_cache
import sys
from pathlib import Path


@lru_cache(maxsize=1)  # Cache for 'single' lookup
def get_root_path() -> Path:
    """
    Get path to the project root
    """
    if hasattr(sys, "_MEIPASS"):
        path = Path(sys._MEIPASS)  # pyright: ignore[reportAttributeAccessIssue]
    else:
        path = Path(__file__).parents[1]  # ./..

    return path
