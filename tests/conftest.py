"""Common test functions."""
from pathlib import Path
from unittest.mock import patch

import pytest


# The test makes a fake index with an arbitrary set of wheels and versions based on
# behavior the tests need to exercise. The test will adjust the input packages and
# versions to exercise different corner cases.
TEST_INDEX_FILES = [
    "aiohttp-3.6.0-cp310-cp310-musllinux_1_2_i686.whl",
    "aiohttp-3.6.1-cp310-cp310-musllinux_1_2_x86_64.whl",
    "aiohttp-3.7.3-cp310-cp310-musllinux_1_2_x86_64.whl",
    "aiohttp-3.7.4-cp310-cp310-musllinux_1_2_x86_64.whl",
    "google_cloud_pubsub-2.1.0-py2.py3-none-any.whl",
    "grpcio-1.31.0-cp310-cp310-musllinux_1_2_x86_64.whl",
    "aioconsole-0.4.1-py3-none-any.whl",
    "aioconsole-0.4.2-py3-none-any.whl",
]


@pytest.fixture(autouse=True)
def mock_index_data():
    """Prepares a fake existing wheel index for use in tests."""
    # Mimc the HTML of a webserver autoindex.
    content = "\n".join(
        f'<a href="{wheel}">{wheel}</a>     28-May-2021 09:53  38181515'
        for wheel in TEST_INDEX_FILES
    )
    with patch("builder.infra.requests.get") as mock_request_get:
        mock_request_get.return_value.status_code = 200
        mock_request_get.return_value.text = content
        yield


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


@pytest.fixture
def tmppath(tmpdir):
    return Path(tmpdir)
