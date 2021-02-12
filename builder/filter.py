"""Filter requirements."""
from pathlib import Path

from builder.pip import write_requirement, parse_requirements

FILTERED = {"RPi.GPIO": ["amd64", "i386", "armhf"]}


def filter_requirements(requirement: Path, arch: str) -> None:
    """Filter requirements."""
    requirements = parse_requirements(requirement)

    for req_filter in FILTERED:
        if arch in FILTERED[req_filter]:
            for req in requirements:
                if req.startswith(req_filter):
                    requirements.remove(req)

    write_requirement(requirement, requirements)
