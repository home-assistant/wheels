"""Utils for wheel."""
from contextlib import suppress
from pathlib import Path
import re
import shutil
from tempfile import TemporaryDirectory

from .utils import run_command, build_arch, build_abi, alpine_version


_RE_LINUX_PLATFORM = re.compile(r"-linux_\w+\.whl$")
_RE_MUSLLINUX_PLATFORM = re.compile(
    r"-musllinux_(?P<major>\d)_(?P<minor>\d)_(?P<arch>\w+)\.whl$"
)

_ARCH_PLAT = {
    "amd64": "x86_64",
    "i386": "i686",
    "aarch64": "aarch64",
    "armhf": "armv6l",
    "armv7": "armv7l",
}

_ALPINE_PLATFORM = {("3", "16"): "musllinux_1_2"}


def check_abi_platform(abi: str, platform: str) -> bool:
    """Return True if abi and platform work."""
    arch = build_arch()
    sys_abi = build_abi()
    sys_platform = _ALPINE_PLATFORM[alpine_version()]

    # Check platform
    if platform == "any":
        pass
    elif platform != f"{sys_platform}_{arch}":
        return False

    # Check abi
    if abi == "none":
        pass
    elif abi != sys_abi:
        return False

    return True


def copy_wheels_from_cache(cache_folder: Path, wheels_folder: Path) -> None:
    """Preserve wheels from cache on timeout error."""
    for wheel_file in cache_folder.glob("**/*.whl"):
        with suppress(OSError):
            shutil.copy(wheel_file, wheels_folder)


def run_auditwheel(wheels_folder: Path) -> None:
    """Run auditwheel to include shared library."""
    with TemporaryDirectory() as temp_dir:
        for wheel_file in wheels_folder.glob("*.whl"):
            if not _RE_LINUX_PLATFORM.search(wheel_file.name):
                continue
            run_command(f"auditwheel repair -w {temp_dir} {wheel_file}")

        # Copy back wheels & make sure ARCH is correct
        target_arch = _ARCH_PLAT[build_arch()]
        for wheel_file in Path(temp_dir).glob("*.whl"):
            package = _RE_MUSLLINUX_PLATFORM.search(wheel_file.name)
            if not package:
                raise RuntimeError(f"Wheel format error {wheel_file}")
            if package["arch"] != target_arch:
                raise RuntimeError(f"Wheel have wrong platform {package['arch']}")
            shutil.copy(wheel_file, wheels_folder)

    # Cleanup linux_ARCH tags
    for wheel_file in wheels_folder.glob("*.whl"):
        if not _RE_LINUX_PLATFORM.search(wheel_file.name):
            continue
        wheel_file.unlink()
