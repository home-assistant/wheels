"""Tests for pip module."""
from pathlib import Path
from builder import pip


def test_parse_requirements():
    assert sorted(
        pip.parse_requirements(
            Path(__file__).parent / "requirements/requirements_all.txt"
        )
    ) == ["RPi.GPIO==1.2.3", "aiohttp==1.2.3", "aiohue==5.6.7"]


def test_extract_packages():
    assert sorted(
        pip.extract_packages(
            Path(__file__).parent / "requirements/requirements_all.txt"
        )
    ) == ["RPi.GPIO==1.2.3", "aiohttp==1.2.3", "aiohue==5.6.7"]


def test_extract_packages_diff():
    assert (
        sorted(
            pip.extract_packages(
                Path(__file__).parent / "requirements/requirements_all.txt",
                Path(__file__).parent / "requirements/requirements_diff.txt",
            )
        )
        == ["RPi.GPIO==1.2.3", "aiohue==5.6.7"]
    )


def test_extract_packages_diff2():
    assert (
        sorted(
            pip.extract_packages(
                Path(__file__).parent / "requirements/requirements_all.txt",
                Path(__file__).parent / "requirements/requirements_all.txt",
            )
        )
        == []
    )
