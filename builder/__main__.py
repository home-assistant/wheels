"""Hass.io Builder main application."""
from pathlib import Path
from tempfile import TemporaryDirectory

import click
import click_pathlib

from .pip import build_wheels
from .upload import run_upload


@click.command()
@click.option("--index", required=True, help="Index URL of remote wheels repository")
@click.option("--requirement", required=True, type=click_pathlib.Path, help="Python requirement file")
@click.option("--upload", default="rsync", help="Upload plugin to upload wheels.")
@click.option("--remote", required=True, type=str, help="Remote URL pass to upload plugin.")
def builder(index, requirement, upload, remote):
    """Build wheels precompiled for Home Assistant container."""

    with TemporaryDirectory() as temp_dir:
        output = Path(temp_dir)

        build_wheels(requirement, index, output)
        run_upload(upload, output, remote)


if __name__ == "__main__":
    builder()
