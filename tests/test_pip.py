"""Tests for pip module."""
from pathlib import Path
from builder import pip


def test_parse_requirements():
    assert sorted(
        pip.parse_requirements(
            Path(__file__).parent / "requirements/requirements_all.txt"
        )
    ) == ["aiohttp==1.2.3", "aiohue==5.6.7"]
