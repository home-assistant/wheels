"""Upload plugin rsync."""

from __future__ import annotations

from pathlib import Path

from ..utils import run_command


def upload(local: Path, remote: str) -> None:
    """Upload wheels from folder to remote rsync server."""
    run_command(
        f"rsync --human-readable --recursive --progress --checksum {local}/* {remote}/",
    )
