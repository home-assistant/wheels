"""Some utils for builder."""
import os
from pathlib import Path
import subprocess
import sys
from typing import Dict, Optional

import requests


_MAP_PEP_ARCHS = {
    "amd64": "x86_64",
    "i386": "i686",
    "aarch64": "aarch64",
    "armv7": "armv7l",
    "armhf": "armv6l",
}

_MAP_PEP_TAG = {"3.16": "musllinux_1_2"}


def alpine_version() -> str:
    """Return alpine version for index server."""
    version = Path("/etc/alpine-release").read_text(encoding="utf-8").split(".")

    return f"alpine-{version[0]}.{version[1]}"


def build_arch() -> str:
    """Return build arch for wheels."""
    return os.environ["ARCH"]


def check_url(url: str) -> None:
    """Check if url is responsible."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()


def run_command(
    cmd: str, env: Optional[Dict[str, str]] = None, timeout: Optional[int] = None
) -> None:
    """Implement subprocess.run but handle timeout different."""
    subprocess.run(
        cmd,
        shell=True,
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=env,
        timeout=timeout,
    )
