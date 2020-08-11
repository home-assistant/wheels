"""Utils for wheel."""
from contextlib import suppress
from pathlib import Path
import re
import shutil

from .utils import run_command, build_arch

RE_WHEEL_PLATFORM = re.compile(r"^(?P<name>.*-)cp\d{2}m?-linux_\w+\.whl$")


ARCH_PLAT = {
    "amd64": "linux_x86_64",
    "i386": "linux_i686",
    "aarch64": "linux_aarch64",
    "armhf": "linux_armv7l",
    "armv7": "linux_armv7l",
}


def fix_wheels_name(wheels_folder: Path) -> None:
    """Remove platform tag from filename."""
    for package in wheels_folder.glob("*.whl"):
        match = RE_WHEEL_PLATFORM.match(package.name)
        if not match:
            continue
        package.rename(Path(package.parent, f"{match.group('name')}none-any.whl"))


def copy_wheels_from_cache(cache_folder: Path, wheels_folder: Path) -> None:
    """Preserve wheels from cache on timeout error."""
    for wheel_file in cache_folder.glob("**/*.whl"):
        with suppress(OSError):
            shutil.copy(wheel_file, wheels_folder)


def run_auditwheel(wheels_folder: Path) -> None:
    """Run auditwheel to include shared library."""
    platform = ARCH_PLAT[build_arch()]

    for wheel_file in wheels_folder.glob("*.whl"):
        if not RE_WHEEL_PLATFORM.match(wheel_file.name):
            continue
        run_command(
            f"auditwheel repair --plat {platform} --no-update-tags -w {wheels_folder} {wheel_file}"
        )
