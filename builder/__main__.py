"""Hass.io Builder main application."""
from pathlib import Path
import shutil
from subprocess import CalledProcessError
import sys
from tempfile import TemporaryDirectory
from time import monotonic
from typing import Optional

import click
import click_pathlib

from builder.apk import install_apks
from builder.infra import create_wheels_folder, create_wheels_index
from builder.pip import (
    build_wheels_local,
    build_wheels_package,
    build_wheels_requirement,
    extract_packages,
    write_requirement,
)
from builder.upload import run_upload
from builder.utils import check_url, fix_wheels_name


@click.command("builder")
@click.option("--apk", default="build-base", help="APKs they are needed to build this.")
@click.option("--index", required=True, help="Index URL of remote wheels repository.")
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
def builder(
    apk: str,
    index: str,
    requirement: Optional[Path],
    requirement_diff: Optional[Path],
    prebuild_dir: Optional[Path],
    single: bool,
    local: bool,
    upload: str,
    remote: str,
):
    """Build wheels precompiled for Home Assistant container."""
    install_apks(apk)
    check_url(index)

    exit_code = 0
    with TemporaryDirectory() as temp_dir:
        output = Path(temp_dir)

        wheels_dir = create_wheels_folder(output)
        wheels_index = create_wheels_index(index)

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
            timer = 0
            for package in packages:
                print(f"Process package: {package}", flush=True)
                try:
                    build_wheels_package(package, wheels_index, wheels_dir)
                except CalledProcessError:
                    exit_code = 109

                if timer < monotonic():
                    run_upload(upload, output, remote)
                    timer = monotonic() + 900
        else:
            # Build all needed wheels at once
            packages = extract_packages(requirement, requirement_diff)
            temp_requirement = Path("/tmp/wheels_requirement.txt")
            write_requirement(temp_requirement, packages)

            try:
                build_wheels_requirement(temp_requirement, wheels_index, wheels_dir)
            except CalledProcessError:
                exit_code = 109

        fix_wheels_name(wheels_dir)
        run_upload(upload, output, remote)

    sys.exit(exit_code)


if __name__ == "__main__":
    builder()  # pylint: disable=no-value-for-parameter
