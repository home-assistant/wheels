"""Upload plugin S3."""
from pathlib import Path
import os

from ..utils import run_command

DEFAULT_REMOTE = os.environ.get(
    "WHEELS_BUILDER_UPLOAD_PLUGIN_REMOTE_S3",
    "https://dc9f963dfa4a630ca83eda7ccd8f363d.r2.cloudflarestorage.com/python-wheels",
)


def upload(local: Path, remote: str = DEFAULT_REMOTE) -> None:
    """Upload wheels from folder to S3 bucket."""
    remote_parts = remote.split("/")
    command = f"s3pypi {local}/* --bucket {remote_parts[-1]}"

    if len(remote_parts) > 1:
        command += f" --s3-endpoint-url {'/'.join(remote_parts[0:-1])}"

    run_command(command)
