"""Utils for wheel."""
from contextlib import suppress
from pathlib import Path
import re
import shutil
from tempfile import TemporaryDirectory

from .utils import run_command, build_arch


_RE_WHEEL_PLATFORM = re.compile(r"^(?P<name>.*-)cp\d{2}m?-linux_\w+\.whl$")

_ARCH_PLAT = {
    "amd64": "x86_64",
    "i386": "i686",
    "aarch64": "aarch64",
    "armhf": "armv7l",
    "armv7": "armv6l",
}

_ALPINE_MUSL_TAG = {"3.16": "musllinux_1_2"}


def fix_wheels_name(wheels_folder: Path) -> None:
    """Remove platform tag from filename."""
    for package in wheels_folder.glob("*.whl"):
        match = _RE_WHEEL_PLATFORM.match(package.name)
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
    with TemporaryDirectory() as temp_dir:
        for wheel_file in wheels_folder.glob("*.whl"):
            if "musllinux" in wheel_file.name:
                continue
            run_command(f"auditwheel repair -w {temp_dir} {wheel_file}")

        # Fix architecture
        # Qemu armv6 looks like armv7
        # FIXME
        target_arch = _ARCH_PLAT[build_arch()]
