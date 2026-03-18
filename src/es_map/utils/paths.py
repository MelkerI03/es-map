from functools import lru_cache
import sys
from pathlib import Path


def _find_project_root(start: Path | None = None) -> Path:
    """
    Walk upward from `start` until a project root marker is found.
    """
    if start is None:
        start = Path(__file__).resolve()

    for parent in [start, *start.parents]:
        if (parent / "pyproject.toml").exists():
            return parent

    raise RuntimeError("Could not find project root")


@lru_cache(maxsize=1)  # Cache for 'single' lookup
def get_root_path() -> Path:
    """
    Get a path the project root
    """
    if hasattr(sys, "_MEIPASS"):
        path = Path(sys._MEIPASS)  # pyright: ignore[reportAttributeAccessIssue]
    else:
        path = _find_project_root()

    return path
