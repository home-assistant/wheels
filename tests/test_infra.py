"""Tests for infra module.

pip module."""
import pytest
from builder.infra import check_available_binary
from unittest.mock import patch


# The test makes a fake index with an arbitrary set of wheels and versions based on
# behavior the tests need to exercise. The test will adjust the input packages and
# versions to exercise different corner cases.
TEST_INDEX_URL = "http://example"
TEST_INDEX_FILES = [
    "aiohttp-3.6.1-cp38-none-any.whl",
    "aiohttp-3.7.3-cp38-none-any.whl",
    "aiohttp-3.7.4-cp38-none-any.whl",
    "google_cloud_pubsub-2.1.0-py2.py3-none-any.whl",
    "grpcio-1.31.0-cp39-none-any.whl",
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


def test_check_available_binary_none() -> None:
    """No-op when no binaries specified to skip."""
    assert (
        check_available_binary(
            TEST_INDEX_URL,
            ":none:",
            packages=[
                "aiohttp==3.7.4",
                "google_cloud_pubsub==2.1.0",
            ],
            constraints=[],
        )
        == ":none:"
    )


def test_check_available_binary_all() -> None:
    """This tool does not allow skipping all binaries."""
    assert (
        check_available_binary(
            TEST_INDEX_URL,
            ":all:",
            packages=[
                "aiohttp==3.7.4",
                "google_cloud_pubsub==2.1.0",
            ],
            constraints=[],
        )
        == ":none:"
    )


def test_check_available_binary_version_present() -> None:
    """Test to skip a binary where the package version is already in the index."""
    assert (
        check_available_binary(
            TEST_INDEX_URL,
            "aiohttp",
            packages=[
                "aiohttp==3.7.4",
                "google_cloud_pubsub==2.1.0",
            ],
            constraints=[],
        )
        == ":none:"
    )


def test_check_available_binary_version_missing() -> None:
    """Test to skip a binary where the package version is not in the index."""
    assert (
        check_available_binary(
            TEST_INDEX_URL,
            "aiohttp",
            packages=[
                "aiohttp==3.7.5",  # Not in the index
                "google_cloud_pubsub==2.1.0",
            ],
            constraints=[],
        )
        == "aiohttp"
    )


def test_check_available_binary_implicit_dep_skipped() -> None:
    """Test case where skip binary lists an implicit dep which is ignored."""
    assert (
        check_available_binary(
            TEST_INDEX_URL,
            "aiohttp,grpcio",
            packages=[
                "aiohttp==3.7.4",
                "google_cloud_pubsub==2.1.0",
            ],
            constraints=[],
        )
        == ":none:"
    )


def test_check_available_binary_skip_constraint() -> None:
    """Test case where skip binary is for constraint in the index."""
    assert (
        check_available_binary(
            TEST_INDEX_URL,
            "aiohttp,grpcio",
            packages=[
                "aiohttp==3.7.4",
                "google_cloud_pubsub==2.1.0",
            ],
            constraints=[
                "grpcio==1.31.0",  # Already exists in index
            ],
        )
        == ":none:"
    )


def test_check_available_binary_for_missing_constraint() -> None:
    """Test case where skip binary is for constraint notin the index."""
    assert (
        check_available_binary(
            TEST_INDEX_URL,
            "aiohttp,grpcio",
            packages=[
                "aiohttp==3.7.4",
                "google_cloud_pubsub==2.1.0",
            ],
            constraints=[
                "grpcio==1.43.0",  # Not in index
            ],
        )
        == "grpcio"
    )
