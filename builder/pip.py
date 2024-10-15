"""Pip build commands."""

from __future__ import annotations

import os
from pathlib import Path

from .utils import run_command


def build_wheels_package(
    package: str,
    index: str,
    output: Path,
    skip_binary: str,
    timeout: int,
    constraint: Path | None = None,
) -> None:
    """Build wheels from a requirements file into output."""
    cpu = os.cpu_count() or 4

    # Modify speed
    build_env = os.environ.copy()
    build_env["MAKEFLAGS"] = f"-j{cpu}"

    # Add constraint
    constraint_cmd = f"--constraint {constraint}" if constraint else ""

    run_command(
        f'pip3 wheel --no-clean --no-binary "{skip_binary}" --wheel-dir {output} --extra-index-url {index} {constraint_cmd} "{package}"',
        env=build_env,
        timeout=timeout,
    )


def build_wheels_requirement(
    requirement: Path,
    index: str,
    output: Path,
    skip_binary: str,
    timeout: int,
    constraint: Path | None = None,
) -> None:
    """Build wheels from a requirements file into output."""
    cpu = os.cpu_count() or 4

    # Modify speed
    build_env = os.environ.copy()
    build_env["MAKEFLAGS"] = f"-j{cpu}"

    # Add constraint
    constraint_cmd = f"--constraint {constraint}" if constraint else ""

    run_command(
        f'pip3 wheel --no-clean --no-binary "{skip_binary}" --wheel-dir {output} --extra-index-url {index} {constraint_cmd} --requirement {requirement}',
        env=build_env,
        timeout=timeout,
    )


def build_wheels_local(
    index: str,
    output: Path,
) -> None:
    """Build wheels from a requirements file into output."""
    cpu = os.cpu_count() or 4

    # Modify speed
    build_env = os.environ.copy()
    build_env["MAKEFLAGS"] = f"-j{cpu}"

    run_command(
        f"pip3 wheel --no-clean --wheel-dir {output} --extra-index-url {index} .",
        env=build_env,
    )


def parse_requirements(requirement: Path) -> list[str]:
    """Parse a requirement files into an array."""
    requirement_list: set[str] = set()
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
    requirement: Path, requirement_diff: Path | None = None
) -> list[str]:
    """Extract packages they need build."""
    packages = parse_requirements(requirement)

    # Without diff
    if requirement_diff is None:
        return packages

    packages_diff = parse_requirements(requirement_diff)

    return list(set(packages) - set(packages_diff))


def write_requirement(requirement: Path, packages: list[str]) -> None:
    """Write packages list to a requirement file."""
    requirement.write_text("\n".join(packages))


def install_pips(index: str, pips: str) -> None:
    """Install all pipy string formated as 'package1;package2'."""
    packages = " ".join(pips.split(";"))

    run_command(
        f"pip install --upgrade --extra-index-url {index} {packages}",
    )
