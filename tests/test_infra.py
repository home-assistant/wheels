"""Tests for infra module."""

from pathlib import Path

from builder import infra


def test_extract_packages_from_index() -> None:
    """Test index package extraction."""
    package_index = infra.extract_packages_from_index("https://example.com")
    assert list(package_index.keys()) == [
        "aiohttp",
        "google_cloud_pubsub",
        "grpcio",
        "aioconsole",
    ]

    assert list(str(package.version) for package in package_index["aiohttp"]) == [
        "3.6.1",
        "3.7.3",
        "3.7.4",
    ]


def test_check_available_binary_none() -> None:
    """No-op when no binaries specified to skip."""
    package_index = infra.extract_packages_from_index("https://example.com")
    assert (
        infra.check_available_binary(
            package_index,
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
    package_index = infra.extract_packages_from_index("https://example.com")
    assert (
        infra.check_available_binary(
            package_index,
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
    package_index = infra.extract_packages_from_index("https://example.com")
    assert (
        infra.check_available_binary(
            package_index,
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
    package_index = infra.extract_packages_from_index("https://example.com")
    assert (
        infra.check_available_binary(
            package_index,
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
    package_index = infra.extract_packages_from_index("https://example.com")
    assert (
        infra.check_available_binary(
            package_index,
            "aiohttp;grpcio",
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
    package_index = infra.extract_packages_from_index("https://example.com")
    assert (
        infra.check_available_binary(
            package_index,
            "aiohttp;grpcio",
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
    """Test case where skip binary is for constraint not in the index."""
    package_index = infra.extract_packages_from_index("https://example.com")
    assert (
        infra.check_available_binary(
            package_index,
            "aiohttp;grpcio",
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


def test_remove_local_wheel(tmppath: Path) -> None:
    """Test removing an existing wheel."""
    package_index = infra.extract_packages_from_index("https://example.com")

    p = tmppath / "google_cloud_pubsub-2.9.0-py2.py3-none-any.whl"
    p.touch()
    p = tmppath / "grpcio-1.31.0-cp310-cp310-musllinux_1_2_x86_64.whl"
    p.touch()
    assert {p.name for p in tmppath.glob("*.whl")} == {
        "grpcio-1.31.0-cp310-cp310-musllinux_1_2_x86_64.whl",
        "google_cloud_pubsub-2.9.0-py2.py3-none-any.whl",
    }

    infra.remove_local_wheels(
        package_index,
        skip_exists=["grpcio"],
        packages=[
            "google_cloud_pubsub==2.9.0",
            "grpcio==1.31.0",  # Exists in index
        ],
        wheels_dir=tmppath,
    )

    # grpcio is removed
    assert {p.name for p in tmppath.glob("*.whl")} == {
        "google_cloud_pubsub-2.9.0-py2.py3-none-any.whl",
    }


def test_remove_local_wheel_preserves_newer(tmppath: Path) -> None:
    """Test that the wheel is preserved when newer than in the index."""
    package_index = infra.extract_packages_from_index("https://example.com")

    p = tmppath / "google_cloud_pubsub-2.9.0-py2.py3-none-any.whl"
    p.touch()
    p = tmppath / "grpcio-1.43.0-cp310-cp310-musllinux_1_2_x86_64.whl"
    p.touch()
    assert {p.name for p in tmppath.glob("*.whl")} == {
        "grpcio-1.43.0-cp310-cp310-musllinux_1_2_x86_64.whl",
        "google_cloud_pubsub-2.9.0-py2.py3-none-any.whl",
    }

    infra.remove_local_wheels(
        package_index,
        skip_exists=["grpcio"],
        packages=[
            "google_cloud_pubsub==2.9.0",
            "grpcio==1.43.0",  # Newer than index
        ],
        wheels_dir=tmppath,
    )

    # grpcio is not removed
    assert {p.name for p in tmppath.glob("*.whl")} == {
        "grpcio-1.43.0-cp310-cp310-musllinux_1_2_x86_64.whl",
        "google_cloud_pubsub-2.9.0-py2.py3-none-any.whl",
    }
