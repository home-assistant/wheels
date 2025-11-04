"""Supported upload function."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def run_upload(plugin_name: str, local: Path, remote: str) -> None:
    """Load a plugin and start upload."""
    plugin = import_module(f".{plugin_name}", "builder.upload")

    # Run upload
    plugin.upload(local, remote)
