"""Tests for pip module."""
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
