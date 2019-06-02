"""Hass.io Builder main application."""
import sys
from pathlib import Path
from subprocess import CalledProcessError
from tempfile import TemporaryDirectory
from time import monotonic

import click
import click_pathlib

from builder.apk import install_apks
from builder.infra import create_wheels_folder, create_wheels_index
from builder.pip import build_wheels, extract_packages
from builder.upload import run_upload
from builder.utils import check_url


@click.command()
@click.option("--apk", default="build-base", help="APKs they are needed to build this.")
@click.option("--index", required=True, help="Index URL of remote wheels repository.")
@click.option(
    "--requirement",
    required=True,
    type=click_pathlib.Path(exists=True),
    help="Python requirement file.",
)
@click.option("--upload", default="rsync", help="Upload plugin to upload wheels.")
@click.option(
    "--remote", required=True, type=str, help="Remote URL pass to upload plugin."
)
@click.option(
    "--requirement-diff",
    type=click_pathlib.Path(exists=True),
    help="Python requirement file to calc the different for selective builds.",
)
def builder(apk, index, requirement, upload, remote, requirement_diff):
    """Build wheels precompiled for Home Assistant container."""
    install_apks(apk)
    check_url(index)

    exit_code = 0
    timer = 0
    with TemporaryDirectory() as temp_dir:
        output = Path(temp_dir)

        wheels_dir = create_wheels_folder(output)
        wheels_index = create_wheels_index(index)
        packages = extract_packages(requirement, requirement_diff)

        for package in packages:
            print(f"Process package: {package}", flush=True)
            try:
                build_wheels(package, wheels_index, wheels_dir)
            except CalledProcessError:
                exit_code = 109

            if timer < monotonic():
                run_upload(upload, output, remote)
                timer = monotonic() + 900

        run_upload(upload, output, remote)

    sys.exit(exit_code)


if __name__ == "__main__":
    builder()  # pylint: disable=no-value-for-parameter
