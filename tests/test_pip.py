"""Tests for pip module."""

from pathlib import Path

from builder import pip


def test_parse_requirements() -> None:
    assert sorted(
        pip.parse_requirements(
            Path(__file__).parent / "requirements/requirements_all.txt",
        ),
    ) == ["RPi.GPIO==1.2.3", "aiohttp==4.2.3", "aiohue==5.6.7"]


def test_extract_packages() -> None:
    assert sorted(
        pip.extract_packages(
            Path(__file__).parent / "requirements/requirements_all.txt",
        ),
    ) == ["RPi.GPIO==1.2.3", "aiohttp==4.2.3", "aiohue==5.6.7"]


def test_extract_packages_diff() -> None:
    assert sorted(
        pip.extract_packages(
            Path(__file__).parent / "requirements/requirements_all.txt",
            Path(__file__).parent / "requirements/requirements_diff.txt",
        ),
    ) == ["RPi.GPIO==1.2.3", "aiohue==5.6.7"]


def test_extract_packages_diff2() -> None:
    assert (
        sorted(
            pip.extract_packages(
                Path(__file__).parent / "requirements/requirements_all.txt",
                Path(__file__).parent / "requirements/requirements_all.txt",
            ),
        )
        == []
    )
