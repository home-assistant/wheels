"""Create folder structure for index."""
from pathlib import Path

from .utils import alpine_version, build_arch


def create_wheels_folder(base_folder: Path) -> Path:
    """Create index structure."""
    wheels_dir = Path(
        base_folder, alpine_version(), build_arch()
    )

    wheels_dir.mkdir(parents=True, exist_ok=True)
    return wheels_dir


def create_wheels_index(base_index: str) -> str:
    """Create wheels specific URL."""
    return f"{base_index}/{alpine_version()}/{build_arch()}/"
