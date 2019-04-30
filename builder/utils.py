"""Some utils for builder."""
from pathlib import Path
import os


def alpine_version() -> str:
    """Return alpine version for index server."""
    version = Path("/etc/alpine-release").read_text().split(".")

    return f"alpine-{version[0]}.{version[1]}"


def build_arch() -> str:
    """Return build arch for wheels."""
    return os.environ["ARCH"]
