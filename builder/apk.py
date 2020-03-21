"""Install APKs for build on host system."""
import subprocess
import sys


def install_apks(apks: str) -> None:
    """Install all apk string formated as 'package1;package2'."""
    packages = " ".join(apks.split(";"))

    subprocess.run(
        f"apk add --no-progress --no-cache {packages}",
        shell=True,
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
