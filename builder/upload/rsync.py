"""Upload plugin rsync."""
from pathlib import Path
import subprocess
import sys

from ..utils import run_command


def upload(local: Path, remote: str) -> None:
    """Upload wheels from folder to remote rsync server."""
    run_command(
        f"rsync --human-readable --recursive --partial --progress --checksum {local}/* {remote}/",
    )
