"""Parsing of run manifests from YAML.

This module owns the file/YAML concern only. It reads a manifest file, ensures
the top level is a mapping, and constructs a :class:`RunManifest`. Validation
errors from Pydantic and I/O or YAML errors are allowed to propagate; the CLI
layer decides how to present them and which exit code to use.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from bio_run_crate.models import RunManifest


def load_manifest(path: Path) -> RunManifest:
    """Read a YAML manifest file and return a validated :class:`RunManifest`.

    Raises:
        ValueError: if the file does not contain a top-level mapping.
        yaml.YAMLError: if the file is not valid YAML.
        pydantic.ValidationError: if the data does not satisfy the model.
        OSError: if the file cannot be read.
    """
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise ValueError(
            f"Manifest must be a YAML mapping at the top level, "
            f"got {type(data).__name__}."
        )

    return RunManifest(**data)
