"""Pip build commands."""
from pathlib import Path
import subprocess
import sys


def build_wheels(requirement: Path, index: str, output: Path) -> None:
    """Build wheels from a requirements file into output."""
    result = subprocess.run(
        f"pip3 wheel --wheel-dir {output} --find-links {index} --requirement {requirement}",
        shell=True, stdout=sys.stdout, stderr=sys.stderr
    )

    # Check result of program
    result.check_returncode()
