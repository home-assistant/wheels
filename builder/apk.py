"""Install APKs for build on host system."""

from __future__ import annotations

import subprocess
import sys


def install_apks(apks: str) -> None:
    """Install all apk string formatted as 'package1;package2'."""
    packages = " ".join(apks.split(";"))

    # Upgrade installed packages to their latest version
    subprocess.run(
        "apk upgrade --no-cache"
        shell=True,
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    subprocess.run(
        f"apk add --no-progress --no-cache {packages}",
        shell=True,
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
