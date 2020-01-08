"""Some utils for builder."""
from pathlib import Path
import os
import re

import requests

RE_WHEEL_PLATFORM = re.compile(r"^(?P<name>.*-)cp\d{2}m?-linux_\w+\.whl$")


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


def fix_wheels_name(wheels_folder: Path) -> None:
    """Remove platform tag from filename."""
    for package in wheels_folder.glob("*.whl"):
        match = RE_WHEEL_PLATFORM.match(package.name)
        if not match:
            continue
        package.rename(Path(package.parent, f"{match.group('name')}none-any.whl"))
