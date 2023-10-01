"""Create folder structure for index."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import List, Set, Dict, Final

from awesomeversion import AwesomeVersion
import requests

from .wheel import check_abi_platform

_RE_REQUIREMENT: Final = re.compile(
    r"(?P<package>.+)(?:==|>|<|<=|>=|~=)(?P<version>.+)"
)
_RE_PACKAGE_INDEX: Final = re.compile(
    r"\"(?P<namever>(?P<name>.+?)-(?P<ver>.+?))(-(?P<build>\d[^-]*))?-(?P<pyver>.+?)-(?P<abi>.+?)-(?P<plat>.+?)\.whl\""
)
_MUSLLINUX: Final = "musllinux"


@dataclass
class WhlPackage:
    """Represent a wheel information from index."""

    name: str
    version: AwesomeVersion
    abi: str
    platform: str


def create_wheels_folder(base_folder: Path) -> Path:
    """Create index structure."""
    wheels_dir = Path(base_folder, _MUSLLINUX)

    wheels_dir.mkdir(parents=True, exist_ok=True)
    return wheels_dir


def create_wheels_index(base_index: str) -> str:
    """Create wheels specific URL with a PEP 503 index."""
    return f"{base_index}/{_MUSLLINUX}-index/"


def create_wheels_list(base_index: str) -> str:
    """Create wheels specific URL that has a list of all wheel files."""
    return f"{base_index}/{_MUSLLINUX}/"


def create_package_map(packages: List[str]) -> Dict[str, AwesomeVersion]:
    """Create a dictionary from package base name to package and version string."""
    results = {}
    for package in packages.copy():
        find = _RE_REQUIREMENT.match(package)
        if not find:
            continue
        package = find["package"]
        version = AwesomeVersion(find["version"])
        results[package] = version
    return results


def extract_packages_from_index(index: str) -> Dict[str, List[WhlPackage]]:
    """Extract packages from index which match the supported."""
    available_data = requests.get(index, allow_redirects=True, timeout=60).text

    result = {}
    for match in _RE_PACKAGE_INDEX.finditer(available_data):
        package = WhlPackage(
            match["name"], AwesomeVersion(match["ver"]), match["abi"], match["plat"]
        )

        if not check_abi_platform(package.abi, package.platform):
            continue
        result.setdefault(package.name, []).append(package)

    return result


def check_existing_packages(
    package_index: Dict[str, List[WhlPackage]], package_map: Dict[str, AwesomeVersion]
) -> Set[str]:
    """Return the set of package names that already exist in the index."""
    found: Set[str] = set({})
    for package, version in package_map.items():
        if package in package_index and any(
            sub_package.version == version for sub_package in package_index[package]
        ):
            found.add(package)
    return found


def check_available_binary(
    package_index: Dict[str, List[WhlPackage]],
    skip_binary: str,
    packages: List[str],
    constraints: List[str],
) -> str:
    """Check if binary exists and ignore this skip."""
    if skip_binary == ":none:":
        return skip_binary

    list_binary = skip_binary.split(";")

    # Map of package basename to the desired package version
    package_map = create_package_map(packages + constraints)

    # View of package map limited to packages in --skip-binary
    binary_package_map = {}
    for binary in list_binary:
        if not (version := package_map.get(binary)):
            print(
                f"Skip binary '{binary}' not in packages/constraints; Can't determine desired version",
                flush=True,
            )
            continue
        binary_package_map[binary] = version

    print(f"Checking if binaries already exist for packages {binary_package_map}")
    list_found: Set[str] = check_existing_packages(package_index, binary_package_map)
    print(f"Packages already exist: {list_found}")
    list_needed = binary_package_map.keys() - list_found

    # Generate needed list of skip binary
    if not list_needed:
        return ":none:"

    print(f"Will force binary build for {list_needed}")
    return ",".join(list_needed)


def remove_local_wheels(
    package_index: Dict[str, List[WhlPackage]],
    skip_exists: List[str],
    packages: List[str],
    wheels_dir: Path,
) -> str:
    """Remove existing wheels if they already exist in the index to avoid syncing."""
    package_map = create_package_map(packages)
    binary_package_map = {
        name: package_map[name] for name in skip_exists if name in package_map
    }
    print(f"Checking if binaries already exist for packages {binary_package_map}")
    exists = check_existing_packages(package_index, binary_package_map)
    for binary in exists:
        version = binary_package_map[binary]
        print(f"Found existing wheels for {binary}, removing local copy {version}")
        for wheel in wheels_dir.glob(f"{binary}-*.whl"):
            print(f"Removing local wheel {wheel}")
            wheel.unlink()
