"""Install APKs for build on host system."""
import subprocess
import sys


def install_apks(apks: str) -> None:
    """Install all apk string formated as 'package1;package2'."""
    packages = " ".join(apks.split(';'))

    result = subprocess.run(
        f"apk add --no-cache {packages}",
        shell=True, stdout=sys.stdout, stderr=sys.stderr
    )

    # Check result of program
    result.check_returncode()
