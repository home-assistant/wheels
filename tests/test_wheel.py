"""Tests for pip module."""

from pathlib import Path

import pytest

from builder import wheel


# pylint: disable=protected-access


@pytest.mark.parametrize(
    "test,result",
    [
        ("cchardet-2.1.7-cp310-cp310-musllinux_1_2_armv7l.whl", "armv7l"),
        ("cchardet-2.1.7-cp310-cp310-musllinux_1_2_x86_64.whl", "x86_64"),
    ],
)
def test_musllinux_regex(test, result):
    """Test musllinux regex."""
    parse = wheel._RE_MUSLLINUX_PLATFORM.search(test)
    assert parse
    assert parse["arch"] == result


@pytest.mark.parametrize(
    "test",
    [
        "cchardet-2.1.7-cp310-cp310-linux_armv7l.whl",
        "cchardet-2.1.7-cp310-cp310-linux_x86_64.whl",
    ],
)
def test_musllinux_regex_wrong(test):
    """Test linux regex."""
    assert wheel._RE_MUSLLINUX_PLATFORM.search(test) is None


@pytest.mark.parametrize(
    "test",
    [
        "cchardet-2.1.7-cp310-cp310-linux_armv7l.whl",
        "cchardet-2.1.7-cp310-cp310-linux_x86_64.whl",
    ],
)
def test_linux_regex(test):
    """Test linux regex."""
    assert wheel._RE_LINUX_PLATFORM.search(test)


@pytest.mark.parametrize(
    "test",
    [
        "cchardet-2.1.7-cp310-cp310-musllinux_1_2_armv7l.whl",
        "cchardet-2.1.7-cp310-cp310-musllinux_1_2_x86_64.whl",
    ],
)
def test_linux_regex_wrong(test):
    """Test linux regex not found."""
    assert wheel._RE_LINUX_PLATFORM.search(test) is None


@pytest.mark.parametrize(
    "abi,platform",
    [
        ("cp310", "musllinux_1_2_x86_64"),
        ("cp310", "musllinux_1_1_x86_64"),
        ("cp310", "musllinux_1_0_x86_64"),
        ("abi3", "musllinux_1_2_x86_64"),
        ("abi3", "musllinux_1_1_x86_64"),
        ("abi3", "musllinux_1_0_x86_64"),
        ("none", "any"),
    ],
)
def test_working_abi_platform(abi, platform):
    """Test working abi/platform variations."""
    assert wheel.check_abi_platform(abi, platform)


@pytest.mark.parametrize(
    "abi,platform",
    [
        ("cp311", "musllinux_1_2_x86_64"),
        ("cp310", "musllinux_1_2_i686"),
        ("cp310", "musllinux_1_3_x86_64"),
        ("abi3", "musllinux_1_3_x86_64"),
    ],
)
def test_not_working_abi_platform(abi, platform):
    """Test not working abi/platform variations."""
    assert not wheel.check_abi_platform(abi, platform)


def test_fix_wheel_unmatch(tmppath: Path) -> None:
    """Test removing an existing wheel that are not match requirements."""

    p = tmppath / "google_cloud_pubsub-2.9.0-py2.py3-none-any.whl"
    p.touch()
    p = tmppath / "grpcio-1.31.0-cp39-cp39-musllinux_1_1_x86_64.whl"
    p.touch()
    assert {p.name for p in tmppath.glob("*.whl")} == {
        "grpcio-1.31.0-cp39-cp39-musllinux_1_1_x86_64.whl",
        "google_cloud_pubsub-2.9.0-py2.py3-none-any.whl",
    }

    assert wheel.fix_wheels_unmatch_requirements(tmppath) == {"grpcio": "1.31.0"}

    # grpc is removed
    assert {p.name for p in tmppath.glob("*.whl")} == {
        "google_cloud_pubsub-2.9.0-py2.py3-none-any.whl",
    }
