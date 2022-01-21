"""Create folder structure for index."""
from pathlib import Path
import re
from typing import List, Set, Dict

import requests

from .utils import alpine_version, build_arch

_RE_REQUIREMENT = re.compile(r"(?P<package>.+)(?:==|>|<|<=|>=|~=)(?P<version>.+)")


def create_wheels_folder(base_folder: Path) -> Path:
    """Create index structure."""
    wheels_dir = Path(base_folder, alpine_version(), build_arch())

    wheels_dir.mkdir(parents=True, exist_ok=True)
    return wheels_dir


def create_wheels_index(base_index: str) -> str:
    """Create wheels specific URL."""
    return f"{base_index}/{alpine_version()}/{build_arch()}/"


def create_package_map(packages: List[str]) -> Dict[str, str]:
    """Create a dictionary from package base name to package and version string."""
    results = {}
    for package in packages.copy():
        find = _RE_REQUIREMENT.match(package)
        if not find:
            continue
        package = find["package"]
        version = find["version"]
        results[package] = f"{package}-{version}"
    return results


def check_existing_packages(index: str, package_map: Dict[str, str]) -> Set[str]:
    """Return the set of package names that already exist in the index."""
    available_data = requests.get(index, allow_redirects=True).text
    found: Set[str] = set({})
    for (binary, package) in package_map.items():
        if package in available_data:
            found.add(binary)
    return found


def check_available_binary(index: str, skip_binary: str, packages: List[str]) -> str:
    """Check if binary exists and ignore this skip."""
    if skip_binary == ":none:":
        return skip_binary

    list_binary = skip_binary.split(",")

    # Map of package basename to the desired package version
    package_map = create_package_map(packages)

    # View of package map limited to packages in --skip-binary
    binary_package_map = {}
    for binary in list_binary:
        if not (package := package_map.get(binary)):
            print(
                f"Skip binary '{binary}' not in packages/constraints; Can't determine desired version",
                flush=True,
            )
            continue
        binary_package_map[binary] = package

    print(f"Checking if binaries already exist for packages {binary_package_map}")
    list_found: Set[str] = check_existing_packages(index, binary_package_map)
    print(f"Packages already exist: {list_found}")
    list_needed = binary_package_map.keys() - list_found

    # Generate needed list of skip binary
    if not list_needed:
        return ":none:"

    print(f"Will force binary build for {list_needed}")
    return ",".join(list_needed)


def remove_local_wheels(
    index: str,
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
    exists = check_existing_packages(index, binary_package_map)
    for binary in exists:
        package = binary_package_map[binary]
        print(f"Found existing wheels for {binary}, removing local copy {package}")
        for wheel in wheels_dir.glob(f"{package}-*.whl"):
            print(f"Removing local wheel {wheel}")
            wheel.unlink()
