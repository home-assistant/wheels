"""Pip build commands."""
import os
from pathlib import Path
import subprocess
import sys
from time import sleep
from typing import List, Optional


def build_wheels_package(
    package: str, index: str, output: Path, skip_binary: str
) -> None:
    """Build wheels from a requirements file into output."""
    cpu = os.cpu_count() or 4

    # Modify speed
    build_env = os.environ.copy()
    build_env["MAKEFLAGS"] = f"-j{cpu}"

    subprocess.run(
        f'pip3 wheel --progress-bar off --no-binary "{skip_binary}" --wheel-dir {output} --find-links {index} "{package}"',
        shell=True,
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=build_env,
    )


def build_wheels_requirement(
    requirement: Path, index: str, output: Path, skip_binary: str
) -> None:
    """Build wheels from a requirements file into output."""
    cpu = os.cpu_count() or 4

    # Modify speed
    build_env = os.environ.copy()
    build_env["MAKEFLAGS"] = f"-j{cpu}"

    subprocess.run(
        f'pip3 wheel --progress-bar off --no-binary "{skip_binary}" --wheel-dir {output} --find-links {index} --requirement {requirement}',
        shell=True,
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=build_env,
    )


def build_wheels_local(index: str, output: Path) -> None:
    """Build wheels from a requirements file into output."""
    cpu = os.cpu_count() or 4

    # Modify speed
    build_env = os.environ.copy()
    build_env["MAKEFLAGS"] = f"-j{cpu}"

    subprocess.run(
        f"pip3 wheel --progress-bar off --wheel-dir {output} --find-links {index} .",
        shell=True,
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=build_env,
    )


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
    latest_exception = None

    # Retry on error
    for _ in range(0, 3):
        try:
            subprocess.run(
                f"pip install --progress-bar off --upgrade --no-cache-dir --prefer-binary --find-links {index} {packages}",
                shell=True,
                check=True,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
        except OSError as err:
            latest_exception = err
            sleep(60)
            continue
        else:
            return

    raise latest_exception
