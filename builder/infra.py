"""Create folder structure for index."""
from pathlib import Path
import re
from typing import List, Set

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


def check_available_binary(index: str, skip_binary: str, packages: List[str]) -> str:
    """Check if binary exists and ignore this skip."""
    if skip_binary == ":none:":
        return skip_binary

    list_binary = skip_binary.split(",")
    available_data = requests.get(index, allow_redirects=True).text

    list_needed: Set[str] = set()
    for binary in list_binary:
        for package in packages:
            if not package.startswith(binary):
                continue
   
            # Check more details
            find = _RE_REQUIREMENT.match(package)
            if find:
                # Check full name
                if binary != find["package"]:
                    continue

                # Process packages
                name = f"{binary}-{find['version']}"
                if name in available_data:
                    continue

            # Ignore binary
            print(f"Binary {package}: {name}", flush=True)
            list_needed.add(binary)

    # Generate needed list of skip binary
    if not list_needed:
        return ":none:"
    return ",".join(list_needed)
