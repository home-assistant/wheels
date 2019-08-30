"""Pip build commands."""
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def build_wheels_package(package: str, index: str, output: Path) -> None:
    """Build wheels from a requirements file into output."""
    cpu = os.cpu_count() or 4

    # Modify speed
    build_env = os.environ.copy()
    build_env["MAKEFLAGS"] = f"-j{cpu}"

    result = subprocess.run(
        f'pip3 wheel --progress-bar ascii --wheel-dir {output} --find-links {index} "{package}"',
        shell=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=build_env,
    )

    # Check result of program
    result.check_returncode()


def build_wheels_requirement(requirement: Path, index: str, output: Path) -> None:
    """Build wheels from a requirements file into output."""
    cpu = os.cpu_count() or 4

    # Modify speed
    build_env = os.environ.copy()
    build_env["MAKEFLAGS"] = f"-j{cpu}"

    result = subprocess.run(
        f"pip3 wheel --progress-bar ascii --wheel-dir {output} --find-links {index} --requirement {requirement}",
        shell=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=build_env,
    )

    # Check result of program
    result.check_returncode()


def build_wheels_local(index: str, output: Path) -> None:
    """Build wheels from a requirements file into output."""
    cpu = os.cpu_count() or 4

    # Modify speed
    build_env = os.environ.copy()
    build_env["MAKEFLAGS"] = f"-j{cpu}"

    result = subprocess.run(
        f"pip3 wheel --progress-bar ascii --wheel-dir {output} --find-links {index} .",
        shell=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=build_env,
    )

    # Check result of program
    result.check_returncode()


def parse_requirements(requirement: Path) -> List[str]:
    """Parse a requirement files into an array."""
    requirement_list = set()
    with requirement.open("r") as data:
        for line in data:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            requirement_list.add(line.split(" ")[-1])
    return list(requirement_list)


def extract_packages(
    requirement: Path, requirement_diff: Optional[Path] = None
) -> List[str]:
    """Extract packages they need build."""
    packages = parse_requirements(requirement)

    # Without diff
    if requirement_diff is None:
        return packages

    packages_diff = parse_requirements(requirement_diff)

    return list(set(packages) - set(packages_diff))


def write_requirement(requirement: Path, packages: List[str]) -> None:
    """Write packages list to a requirement file."""
    requirement.write_text("\n".join(packages))


def install_pips(index: str, pips: str) -> None:
    """Install all pipy string formated as 'package1;package2'."""
    packages = " ".join(pips.split(";"))

    result = subprocess.run(
        f"pip install --upgrade --no-cache-dir --prefer-binary --find-links {index} {packages}",
        shell=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    # Check result of program
    result.check_returncode()
