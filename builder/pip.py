"""Pip build commands."""
import os
import subprocess
import sys
from pathlib import Path
from typing import List


def build_wheels(package: str, index: str, output: Path) -> None:
    """Build wheels from a requirements file into output."""
    cpu = os.cpu_count() or 4

    # Modify speed
    build_env = os.environ.copy()
    build_env["MAKEFLAGS"] = f"-j{cpu}"

    result = subprocess.run(
        f"pip3 wheel --progress-bar ascii --wheel-dir {output} --find-links {index} {package}",
        shell=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=build_env,
    )

    # Check result of program
    result.check_returncode()


def parse_requirements(requirement: Path) -> List[str]:
    """Parse a requirement files into an array."""
    requirement_list = []
    with requirement.open("r") as data:
        for line in data:
            if not line or line.startswith("#"):
                continue
            requirement_list.append(line)
    return requirement_list
