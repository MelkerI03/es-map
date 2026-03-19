import os
from pathlib import Path
import shutil


def overwrite_copy(src: Path, dst: Path) -> None:
    try:
        if dst.exists():
            os.remove(dst)
        shutil.copy(src, dst)
    except PermissionError:
        print(f"File locked: {dst}, skipping...")
