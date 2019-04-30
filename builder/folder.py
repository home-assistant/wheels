"""Create folder structure for index."""
from pathlib import Path
import os

from .utils import python_version, alpine_version


def create_wheels_folder(temp_folder: Path) -> Path:
    """Create index structure."""
    wheels_dir = Path(
        temp_folder, alpine_version(), os.environ["ARCH"], python_version()
    )

    wheels_dir.mkdir(parents=True, exist_ok=True)
    return wheels_dir
