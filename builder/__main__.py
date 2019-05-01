"""Hass.io Builder main application."""
from pathlib import Path
from tempfile import TemporaryDirectory

import click
import click_pathlib

from builder.apk import install_apks
from builder.folder import create_wheels_folder, create_wheels_index
from builder.pip import build_wheels
from builder.upload import run_upload


@click.command()
@click.option(
    "--apk", default="build-base", help="APKs they are needed to build this.")
@click.option(
    "--index", required=True, help="Index URL of remote wheels repository.")
@click.option(
    "--requirement", required=True, type=click_pathlib.Path(exists=True), help="Python requirement file.")
@click.option(
    "--upload", default="rsync", help="Upload plugin to upload wheels.")
@click.option(
    "--remote", required=True, type=str, help="Remote URL pass to upload plugin.")
def builder(apk, index, requirement, upload, remote):
    """Build wheels precompiled for Home Assistant container."""
    install_apks(apk)

    with TemporaryDirectory() as temp_dir:
        output = Path(temp_dir)

        wheels_dir = create_wheels_folder(output)
        wheels_index = create_wheels_index(index)

        build_wheels(requirement, wheels_index, wheels_dir)
        run_upload(upload, output, remote)


if __name__ == "__main__":
    builder()  # pylint: disable=no-value-for-parameter
