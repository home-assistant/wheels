"""Test filter."""
import pytest
from pathlib import Path
from shutil import copyfile

from builder import filter
from builder import pip


@pytest.mark.parametrize(
    "package, arch, result",
    [
        ("RPi.GPIO==1.2.3", "amd64", False),
        ("RPi.GPIO==1.2.3", "i386", False),
        ("RPi.GPIO==1.2.3", "armhf", False),
        ("RPi.GPIO==1.2.3", "armv7", True),
        ("RPi.GPIO==1.2.3", "aarch64", True),
    ],
)
def test_filter(tmpdir, package, arch, result):
    """Test the filter."""
    source_file = Path(__file__).parent / "requirements/requirements.txt"
    dest_file = Path(tmpdir / "requirements.txt")
    copyfile(source_file, f"{tmpdir}/requirements.txt")

    before = pip.extract_packages(dest_file)
    assert package in before

    filter.filter_requirements(dest_file, arch)

    after = pip.extract_packages(dest_file)
    assert (package in after) == result
