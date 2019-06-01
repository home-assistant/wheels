"""Upload plugin rsync."""
from pathlib import Path
import subprocess
import sys


def upload(local: Path, remote: str) -> None:
    """Upload wheels from folder to remote rsync server."""
    result = subprocess.run(
        f"rsync -chrP {local}/* {remote}/",
        shell=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    # Check result of program
    result.check_returncode()
