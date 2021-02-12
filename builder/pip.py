"""Pip build commands."""
import os
from pathlib import Path
from typing import List, Optional
from awesomeversion import AwesomeVersion

from .utils import run_command


def build_wheels_package(
    package: str,
    index: str,
    output: Path,
    skip_binary: str,
    timeout: int,
    alpine: AwesomeVersion,
    constraint: Optional[Path] = None,
) -> None:
    """Build wheels from a requirements file into output."""
    cpu = os.cpu_count() or 4

    # Modify speed
    build_env = os.environ.copy()
    build_env["MAKEFLAGS"] = f"-j{cpu}"

    if alpine < "3.13":
        build_env["CRYPTOGRAPHY_DONT_BUILD_RUST"] = "1"

    # Add constraint
    constraint_cmd = f"--constraint {constraint}" if constraint else ""

    run_command(
        f'pip3 wheel --progress-bar off --no-clean --no-binary "{skip_binary}" --wheel-dir {output} --find-links {index} {constraint_cmd} "{package}"',
        env=build_env,
        timeout=timeout,
    )


def build_wheels_requirement(
    requirement: Path,
    index: str,
    output: Path,
    skip_binary: str,
    timeout: int,
    alpine: AwesomeVersion,
    constraint: Optional[Path] = None,
) -> None:
    """Build wheels from a requirements file into output."""
    cpu = os.cpu_count() or 4

    # Modify speed
    build_env = os.environ.copy()
    build_env["MAKEFLAGS"] = f"-j{cpu}"

    if alpine < "3.13":
        build_env["CRYPTOGRAPHY_DONT_BUILD_RUST"] = "1"

    # Add constraint
    constraint_cmd = f"--constraint {constraint}" if constraint else ""

    run_command(
        f'pip3 wheel --progress-bar off --no-clean --no-binary "{skip_binary}" --wheel-dir {output} --find-links {index} {constraint_cmd} --requirement {requirement}',
        env=build_env,
        timeout=timeout,
    )


def build_wheels_local(
    index: str,
    output: Path,
    alpine: AwesomeVersion,
) -> None:
    """Build wheels from a requirements file into output."""
    cpu = os.cpu_count() or 4

    # Modify speed
    build_env = os.environ.copy()
    build_env["MAKEFLAGS"] = f"-j{cpu}"

    if alpine < "3.13":
        build_env["CRYPTOGRAPHY_DONT_BUILD_RUST"] = "1"

    run_command(
        f"pip3 wheel --progress-bar off --no-clean --wheel-dir {output} --find-links {index} .",
        env=build_env,
    )


def parse_requirements(requirement: Path) -> List[str]:
    """Parse a requirement files into an array."""
    requirement_list = set()
    with requirement.open("r") as data:
        for line in data:
            line = line.strip()

            # Ignore comments or constraint files
            if not line or line.startswith(("#", "-c")):
                continue

            if not line.startswith("-r"):
                requirement_list.add(line.split(" ")[-1])
                continue

            # References new requirements file
            requirement_list.update(parse_requirements(requirement.parent / line[3:]))

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

    run_command(
        f"pip install --disable-pip-version-check --progress-bar off --upgrade --no-cache-dir --prefer-binary --find-links {index} {packages}",
    )
