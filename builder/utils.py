"""Some utils for builder."""
from pathlib import Path
import os

import requests


def alpine_version() -> str:
    """Return alpine version for index server."""
    version = Path("/etc/alpine-release").read_text().split(".")

    return f"alpine-{version[0]}.{version[1]}"


def build_arch() -> str:
    """Return build arch for wheels."""
    return os.environ["ARCH"]


def check_url(url: str) -> None:
    """Check if url is responsible."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
