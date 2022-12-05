"""Upload plugin rsync."""
import os
from pathlib import Path

from ..utils import run_command

DEFAULT_REMOTE = os.environ.get(
    "WHEELS_BUILDER_UPLOAD_PLUGIN_REMOTE_RSYNC",
    "https://wheels.home-assistant.io",
)


def upload(local: Path, remote: str = DEFAULT_REMOTE) -> None:
    """Upload wheels from folder to remote rsync server."""
    run_command(
        f"rsync --human-readable --recursive --progress --checksum {local}/* {remote}/",
    )
