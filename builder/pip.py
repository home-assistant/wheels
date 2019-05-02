"""Pip build commands."""
from pathlib import Path
import os
import subprocess
import sys


def build_wheels(requirement: Path, index: str, output: Path) -> None:
    """Build wheels from a requirements file into output."""
    cpu = os.cpu_count() or 4

    # Modify speed
    build_env = os.environ.copy()
    build_env['MAKEFLAGS'] = f"-j{cpu}"

    result = subprocess.run(
        f"pip3 wheel --progress-bar ascii --wheel-dir {output} --find-links {index} --requirement {requirement}",
        shell=True, stdout=sys.stdout, stderr=sys.stderr, env=build_env
    )

    # Check result of program
    result.check_returncode()
