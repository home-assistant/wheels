"""Tests for infra module."""

from pathlib import Path

from packaging.utils import canonicalize_name

from builder import infra


def test_extract_packages_from_index() -> None:
    """Test index package extraction."""
    package_index = infra.extract_packages_from_index("https://example.com")
    assert list(package_index.keys()) == [
        "aiohttp",
        "google-cloud-pubsub",
        "grpcio",
        "aioconsole",
    ]

    assert [
        str(package.version) for package in package_index[canonicalize_name("aiohttp")]
    ] == [
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
    """Verify that the tool does not allow skipping all binaries."""
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


def test_check_available_binary_normalized_package_names() -> None:
    """Test package names are normalized before checking package index."""
    package_index = infra.extract_packages_from_index("https://example.com")
    assert list(package_index.keys()) == [  # normalized spelling from index
        "aiohttp",
        "google-cloud-pubsub",
        "grpcio",
        "aioconsole",
    ]
    assert (
        infra.check_available_binary(
            package_index,
            "AIOhttp;GRPcio",
            packages=[
                "aioHTTP==3.7.4",
                "google_cloud-PUBSUB==2.1.0",
            ],
            constraints=[
                "grpcIO==1.31.0",  # Already exists in index
            ],
        )
        == ":none:"
    )


def test_remove_local_wheel(tmp_path: Path) -> None:
    """Test removing an existing wheel."""
    package_index = infra.extract_packages_from_index("https://example.com")

    p = tmp_path / "google_cloud_pubsub-2.9.0-py2.py3-none-any.whl"
    p.touch()
    p = tmp_path / "grpcio-1.31.0-cp310-cp310-musllinux_1_2_x86_64.whl"
    p.touch()
    p = tmp_path / "grpcio-1.31.0-py3-none-any.whl"  # different platform tag
    p.touch()
    p = tmp_path / "some_other_file.txt"  # other files are ignored
    p.touch()
    assert {p.name for p in tmp_path.glob("*.whl")} == {
        "grpcio-1.31.0-cp310-cp310-musllinux_1_2_x86_64.whl",
        "grpcio-1.31.0-py3-none-any.whl",
        "google_cloud_pubsub-2.9.0-py2.py3-none-any.whl",
    }

    infra.remove_local_wheels(
        package_index,
        skip_exists="grpcio",
        packages=[
            "google_cloud_pubsub==2.9.0",
            "grpcio==1.31.0",  # Exists in index
        ],
        wheels_dir=tmp_path,
    )

    # both grpcio wheels are removed
    assert {p.name for p in tmp_path.glob("*.whl")} == {
        "google_cloud_pubsub-2.9.0-py2.py3-none-any.whl",
    }


def test_remove_local_wheel_preserves_newer(tmp_path: Path) -> None:
    """Test that the wheel is preserved when newer than in the index."""
    package_index = infra.extract_packages_from_index("https://example.com")

    p = tmp_path / "google_cloud_pubsub-2.9.0-py2.py3-none-any.whl"
    p.touch()
    p = tmp_path / "grpcio-1.43.0-cp310-cp310-musllinux_1_2_x86_64.whl"
    p.touch()
    assert {p.name for p in tmp_path.glob("*.whl")} == {
        "grpcio-1.43.0-cp310-cp310-musllinux_1_2_x86_64.whl",
        "google_cloud_pubsub-2.9.0-py2.py3-none-any.whl",
    }

    infra.remove_local_wheels(
        package_index,
        skip_exists="grpcio",
        packages=[
            "google_cloud_pubsub==2.9.0",
            "grpcio==1.43.0",  # Newer than index
        ],
        wheels_dir=tmp_path,
    )

    # grpcio is not removed
    assert {p.name for p in tmp_path.glob("*.whl")} == {
        "grpcio-1.43.0-cp310-cp310-musllinux_1_2_x86_64.whl",
        "google_cloud_pubsub-2.9.0-py2.py3-none-any.whl",
    }


def test_remove_local_wheel_normalized_package_names(tmp_path: Path) -> None:
    """Test package names are normalized before removing existing wheels."""
    package_index = infra.extract_packages_from_index("https://example.com")

    p = tmp_path / "google_cloud_pubsub-2.1.0-py2.py3-none-any.whl"
    p.touch()
    p = tmp_path / "grpcio-1.31.0-cp310-cp310-musllinux_1_2_x86_64.whl"
    p.touch()
    assert {p.name for p in tmp_path.glob("*.whl")} == {
        "grpcio-1.31.0-cp310-cp310-musllinux_1_2_x86_64.whl",
        "google_cloud_pubsub-2.1.0-py2.py3-none-any.whl",
    }

    infra.remove_local_wheels(
        package_index,
        skip_exists="GRPcio;GOOGLE-cloud_pubsub",
        packages=[
            "google_cloud-PUBSUB==2.1.0",  # Exists in index
            "grpcIO==1.31.0",  # Exists in index
        ],
        wheels_dir=tmp_path,
    )

    # grpcio and google-cloud-pubsub are removed
    assert {p.name for p in tmp_path.glob("*.whl")} == set()


def test_remove_local_wheel_no_build_wheels(tmp_path: Path) -> None:
    """Test remove_local_wheels does not fail with skip_exists and no build wheels."""
    package_index = infra.extract_packages_from_index("https://example.com")
    assert {p.name for p in tmp_path.glob("*.whl")} == set()

    infra.remove_local_wheels(
        package_index,
        skip_exists="grpcio",
        packages=[
            "grpcio==1.31.0",  # Exists in index
        ],
        wheels_dir=tmp_path,
    )
