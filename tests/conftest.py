"""Common test functions."""
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def sys_arch():
    """Patch system arch."""
    with patch("builder.utils.build_arch", return_value="amd64"), patch(
        "builder.wheel.build_arch", return_value="amd64"
    ):
        yield


@pytest.fixture(autouse=True)
def sys_abi():
    """Patch system abi."""
    with patch("builder.utils.build_abi", return_value="cp310"), patch(
        "builder.wheel.build_abi", return_value="cp310"
    ):
        yield


@pytest.fixture(autouse=True)
def sys_alpine():
    """Patch system abi."""
    with patch("builder.utils.alpine_version", return_value=("3", "16")), patch(
        "builder.wheel.alpine_version", return_value=("3", "16")
    ):
        yield
