"""Some utils for builder."""
from pathlib import Path
import sys

def python_version() -> str:
    """Return python version for index server."""
    return f"{sys.version_info[0]}.{sys.version_info[1]}"

def alpine_version() -> str:
    """Return alpine version for index server."""
    version = Path("/etc/alpine-release").read_text().split(".")

    return f"alpine-{version[0]}.{version[1]}"
