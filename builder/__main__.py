"""Hass.io Builder main application."""
from pathlib import Path
import shutil
from subprocess import CalledProcessError, TimeoutExpired
import sys
from tempfile import TemporaryDirectory
from typing import Optional

import click
import click_pathlib

from builder.apk import install_apks
from builder.infra import (
    create_wheels_list,
    extract_packages_from_index,
    check_available_binary,
    create_wheels_folder,
    create_wheels_index,
    remove_local_wheels,
)
from builder.pip import (
    build_wheels_local,
    build_wheels_package,
    build_wheels_requirement,
    extract_packages,
    install_pips,
    parse_requirements,
    write_requirement,
)
from builder.upload import run_upload
from builder.utils import check_url
from builder.wheel import (
    copy_wheels_from_cache,
    run_auditwheel,
    fix_wheels_unmatch_requirements,
)


@click.command("builder")
@click.option("--apk", type=str, help="APKs they are needed to build this.")
@click.option("--pip", type=str, help="PiPy modules needed to build this.")
@click.option("--index", required=True, help="Index URL of remote wheels repository.")
@click.option(
    "--skip-binary", default=":none:", help="List of packages to skip wheels from pypi."
)
@click.option(
    "--requirement",
    type=click_pathlib.Path(exists=True),
    help="Python requirement file.",
)
@click.option(
    "--requirement-diff",
    type=click_pathlib.Path(exists=True),
    help="Python requirement file to calc the different for selective builds.",
)
@click.option(
    "--constraint",
    type=click_pathlib.Path(exists=True),
    help="Python constraint file.",
)
@click.option(
    "--prebuild-dir",
    type=click_pathlib.Path(exists=True),
    help="Folder with include allready builded wheels for upload.",
)
@click.option(
    "--single",
    is_flag=True,
    default=False,
    help="Install every package as single requirement.",
)
@click.option(
    "--local", is_flag=True, default=False, help="Build wheel from local folder setup."
)
@click.option(
    "--legacy", is_flag=True, default=False, help="Run pip with legacy resolver."
)
@click.option(
    "--test", is_flag=True, default=False, help="Test building wheels, no upload."
)
@click.option("--upload", default="rsync", help="Upload plugin to upload wheels.")
@click.option(
    "--remote", required=True, type=str, help="Remote URL pass to upload plugin."
)
@click.option(
    "--timeout", default=345, type=int, help="Max runtime for pip before abort."
)
def builder(
    apk: Optional[str],
    pip: Optional[str],
    index: str,
    skip_binary: str,
    requirement: Optional[Path],
    requirement_diff: Optional[Path],
    constraint: Optional[Path],
    prebuild_dir: Optional[Path],
    single: bool,
    local: bool,
    legacy: bool,
    test: bool,
    upload: str,
    remote: str,
    timeout: int,
):
    """Build wheels precompiled for Home Assistant container."""
    check_url(index)

    exit_code = 0
    with TemporaryDirectory() as temp_dir:
        output = Path(temp_dir)
        timeout = timeout * 60

        wheels_dir = create_wheels_folder(output)
        wheels_index = create_wheels_index(index)
        wheels_list = create_wheels_list(index)
        package_index = extract_packages_from_index(wheels_list)

        # Setup build helper
        if apk:
            install_apks(apk)
        if pip:
            install_pips(wheels_index, pip)

        if local:
            # Build wheels in a local folder/src
            build_wheels_local(wheels_index, wheels_dir)
        elif prebuild_dir:
            # Prepare allready builded wheels for upload
            for whl_file in prebuild_dir.glob("*.whl"):
                shutil.copy(whl_file, Path(wheels_dir, whl_file.name))
        elif single:
            # Build every wheel like a single installation
            packages = extract_packages(requirement, requirement_diff)
            constraints = parse_requirements(constraint) if constraint else []
            skip_binary_new = check_available_binary(
                package_index,
                skip_binary,
                packages,
                constraints,
            )
            for package in packages:
                print(f"Process package: {package}", flush=True)
                try:
                    build_wheels_package(
                        package,
                        wheels_index,
                        wheels_dir,
                        skip_binary_new,
                        timeout,
                        constraint,
                    )
                except CalledProcessError:
                    exit_code = 109
                except TimeoutExpired:
                    exit_code = 80
        else:
            # Build all needed wheels at once
            packages = extract_packages(requirement, requirement_diff)
            temp_requirement = Path("/tmp/wheels_requirement.txt")
            write_requirement(temp_requirement, packages)
            constraints = parse_requirements(constraint) if constraint else []
            skip_binary_new = check_available_binary(
                package_index,
                skip_binary,
                packages,
                constraints,
            )
            try:
                build_wheels_requirement(
                    temp_requirement,
                    wheels_index,
                    wheels_dir,
                    skip_binary_new,
                    timeout,
                    constraint,
                    legacy,
                )
            except CalledProcessError:
                exit_code = 109
            except TimeoutExpired:
                exit_code = 80

        # pip copy wheels only on success over to our folder
        # let's preserve on a error all success builds before
        if exit_code != 0:
            copy_wheels_from_cache(Path("/root/.cache/pip/wheels"), wheels_dir)

        if not run_auditwheel(wheels_dir):
            exit_code = 109

        # Check if all wheels are on our min requirements
        package_wrong = fix_wheels_unmatch_requirements(wheels_dir)
        if package_wrong and exit_code != 80:
            for package, version in package_wrong.items():
                build_wheels_package(
                    f"{package}=={str(version)}",
                    wheels_index,
                    wheels_dir,
                    package,
                    timeout,
                )
            if not run_auditwheel(wheels_dir):
                exit_code = 109

        if skip_binary != ":none:":
            # Some wheels that already exist should not be overwritten in case we replace with
            # a wheel that came from pypi rather than a wheel built from source with extra flags.
            # When --skip-binary and --skip-exists are set a wheel is only built from source once.
            packages = extract_packages(requirement, requirement_diff)
            constraints = parse_requirements(constraint) if constraint else []
            remove_local_wheels(
                package_index,
                skip_binary.split(";"),
                packages + constraints,
                wheels_dir,
            )

        if not test:
            run_upload(upload, output, remote)

    sys.exit(exit_code)


if __name__ == "__main__":
    builder()  # pylint: disable=no-value-for-parameter
