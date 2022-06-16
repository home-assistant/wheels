"""Some utils for builder."""
from functools import cache
import os
from pathlib import Path
import subprocess
import sys
from typing import Dict, Optional, Tuple

import requests


@cache
def alpine_version() -> Tuple[str, str]:
    """Return alpine version for index server."""
    version = Path("/etc/alpine-release").read_text(encoding="utf-8").split(".")

    return (version[0], version[1])


@cache
def build_arch() -> str:
    """Return build arch for wheels."""
    return os.environ["ARCH"]


@cache
def build_abi() -> str:
    """Return build abi for wheels."""
    return os.environ["ABI"]


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
