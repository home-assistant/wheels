"""Utils for wheel."""

from __future__ import annotations

import re
import shutil
from contextlib import suppress
from functools import cache
from pathlib import Path
from subprocess import CalledProcessError
from tempfile import TemporaryDirectory
from typing import Final

from awesomeversion import AwesomeVersion

from .utils import alpine_version, build_abi, build_arch, run_command

_RE_PACKAGE_FULL: Final = re.compile(
    r"^(?P<namever>(?P<name>.+?)-(?P<ver>.+?))(-(?P<build>\d[^-]*))?-(?P<pyver>.+?)-(?P<abi>.+?)-(?P<plat>.+?)\.whl$",
)
_RE_LINUX_PLATFORM: Final = re.compile(r"-linux_\w+\.whl$")
_RE_MUSLLINUX_PLATFORM: Final = re.compile(
    r"-musllinux_(?P<major>\d)_(?P<minor>\d)_(?P<arch>\w+)\.whl$",
)

_ARCH_PLAT = {
    "amd64": "x86_64",
    "aarch64": "aarch64",
}

_ALPINE_MUSL_VERSION = {
    ("3", "16"): (1, 2),
    ("3", "17"): (1, 2),
    ("3", "18"): (1, 2),
    ("3", "19"): (1, 2),
    ("3", "20"): (1, 2),
    ("3", "21"): (1, 2),
    ("3", "22"): (1, 2),
}


@cache
def sys_platform(arch: str) -> set[str]:
    """Build list of supported platform tags.

    Minor musl versions are backwards compatible.
    """
    major, minor = _ALPINE_MUSL_VERSION[alpine_version()]
    return {"any", *[f"musllinux_{major}_{i}_{arch}" for i in range(minor + 1)]}


def check_abi_platform(abi: str, platform: str) -> bool:
    """Return True if abi and platform work."""
    arch = _ARCH_PLAT[build_arch()]
    sys_abi = build_abi()

    # Check platform
    if platform in sys_platform(arch):
        pass
    else:
        return False

    # Check abi
    if abi in ("none", "abi3", sys_abi):
        pass
    else:
        return False

    return True


def fix_wheels_unmatch_requirements(wheels_folder: Path) -> dict[str, AwesomeVersion]:
    """Check Wheels against our min requirements."""
    result: dict[str, AwesomeVersion] = {}
    for wheel_file in wheels_folder.glob("*.whl"):
        package = _RE_PACKAGE_FULL.fullmatch(wheel_file.name)
        if not package:
            msg = f"Error on parse wheel {wheel_file.name}"
            raise RuntimeError(msg)

        if check_abi_platform(package["abi"], package["plat"]):
            continue

        print(
            f"Found wheel {wheel_file.name} that not match our min requirements",
            flush=True,
        )
        result[package["name"]] = AwesomeVersion(package["ver"])
        wheel_file.unlink()

    return result


def copy_wheels_from_cache(cache_folder: Path, wheels_folder: Path) -> None:
    """Preserve wheels from cache on timeout error."""
    for wheel_file in cache_folder.glob("**/*.whl"):
        with suppress(OSError):
            shutil.copy(wheel_file, wheels_folder)


def run_auditwheel(wheels_folder: Path) -> bool:
    """Run auditwheel to include shared library."""
    success = True
    with TemporaryDirectory() as temp_dir:
        for wheel_file in wheels_folder.glob("*.whl"):
            if not _RE_LINUX_PLATFORM.search(wheel_file.name):
                continue
            try:
                run_command(f"auditwheel repair -w {temp_dir} {wheel_file}")
            except CalledProcessError as err:
                print(f"Issues auditwheel {wheel_file.name}: {err!s}", flush=True)
                success = False
                wheel_file.unlink()

        # Copy back wheels & make sure ARCH is correct
        target_arch = _ARCH_PLAT[build_arch()]
        for wheel_file in Path(temp_dir).glob("*.whl"):
            package = _RE_MUSLLINUX_PLATFORM.search(wheel_file.name)
            if not package:
                msg = f"Wheel format error {wheel_file}"
                raise RuntimeError(msg)
            if package["arch"] != target_arch:
                msg = f"Wheel have wrong platform {package['arch']}"
                raise RuntimeError(msg)
            shutil.copy(wheel_file, wheels_folder)

    # Cleanup linux_ARCH tags
    for wheel_file in wheels_folder.glob("*.whl"):
        if not _RE_LINUX_PLATFORM.search(wheel_file.name):
            continue
        wheel_file.unlink()

    return success
