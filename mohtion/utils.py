"""File system utilities."""
import logging
import os
import shutil
import stat
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

def force_delete_readonly(func: Any, path: str, exc_info: Any) -> None:
    """
    Error handler for shutil.rmtree.

    If the error is due to an access error (read only file),
    it attempts to add write permission and then retries.

    Usage: shutil.rmtree(path, onerror=force_delete_readonly)
    """
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        logger.warning(f"Failed to force delete {path}: {e}")

def cleanup_path(path: Path) -> None:
    """Recursively remove a directory, handling read-only files on Windows."""
    if path.exists():
        shutil.rmtree(path, onerror=force_delete_readonly)
