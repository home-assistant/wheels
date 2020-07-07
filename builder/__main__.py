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
    create_wheels_folder,
    create_wheels_index,
    check_available_binary,
)
from builder.pip import (
    build_wheels_local,
    build_wheels_package,
    build_wheels_requirement,
    extract_packages,
    install_pips,
    write_requirement,
)
from builder.upload import run_upload
from builder.utils import check_url, fix_wheels_name


@click.command("builder")
@click.option("--apk", default="build-base", help="APKs they are needed to build this.")
@click.option("--pip", default="Cython", help="PiPy modules needed to build this.")
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
@click.option("--upload", default="rsync", help="Upload plugin to upload wheels.")
@click.option(
    "--remote", required=True, type=str, help="Remote URL pass to upload plugin."
)
@click.option(
    "--timeout", default=330, type=int, help="Max runtime for pip before abort."
)
def builder(
    apk: str,
    pip: str,
    index: str,
    skip_binary: str,
    requirement: Optional[Path],
    requirement_diff: Optional[Path],
    constraint: Optional[Path],
    prebuild_dir: Optional[Path],
    single: bool,
    local: bool,
    upload: str,
    remote: str,
    timeout: int,
):
    """Build wheels precompiled for Home Assistant container."""
    install_apks(apk)
    check_url(index)

    exit_code = 0
    with TemporaryDirectory() as temp_dir:
        output = Path(temp_dir)

        wheels_dir = create_wheels_folder(output)
        wheels_index = create_wheels_index(index)

        # Setup build helper
        install_pips(wheels_index, pip)
        timeout = timeout * 60

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
            skip_binary = check_available_binary(wheels_index, skip_binary, packages)
            for package in packages:
                print(f"Process package: {package}", flush=True)
                try:
                    build_wheels_package(
                        package,
                        wheels_index,
                        wheels_dir,
                        skip_binary,
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

            skip_binary = check_available_binary(wheels_index, skip_binary, packages)
            try:
                build_wheels_requirement(
                    temp_requirement,
                    wheels_index,
                    wheels_dir,
                    skip_binary,
                    timeout,
                    constraint,
                )
            except CalledProcessError:
                exit_code = 109
            except TimeoutExpired:
                exit_code = 80

        fix_wheels_name(wheels_dir)
        run_upload(upload, output, remote)

    sys.exit(exit_code)


if __name__ == "__main__":
    builder()  # pylint: disable=no-value-for-parameter
