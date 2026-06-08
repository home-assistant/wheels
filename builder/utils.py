"""Some utils for builder."""

from __future__ import annotations

import inspect
import os
import subprocess
import sys
from functools import cache
from pathlib import Path

import requests


@cache
def alpine_version() -> tuple[str, str]:
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
    cmd: str,
    env: dict[str, str] | None = None,
    timeout: int | None = None,
) -> None:
    """Implement subprocess.run but handle timeout different."""
    stack = inspect.stack()
    print(
        f"::group::"
        f"{Path(*Path(stack[1].filename).parts[-2:])}:{stack[1].function}"
        " => "
        f"{Path(*Path(stack[0].filename).parts[-2:])}:{stack[0].function}"
        "\n"
        f"subprocess.run(\n"
        f"    cmd={cmd},\n"
        f"    env={'***' if env else env},\n"
        f"    timeout={timeout}\n"
        f")\n"
        f"::endgroup::\n",
    )

    subprocess.run(  # noqa: S602
        cmd,
        shell=True,
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=env,
        timeout=timeout,
    )
