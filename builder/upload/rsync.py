"""Upload plugin rsync."""

from __future__ import annotations

from typing import TYPE_CHECKING

from builder.utils import run_command

if TYPE_CHECKING:
    from pathlib import Path


def upload(local: Path, remote: str) -> None:
    """Upload wheels from folder to remote rsync server."""
    run_command(
        f"rsync --human-readable --recursive --progress --checksum {local}/* {remote}/",
    )
