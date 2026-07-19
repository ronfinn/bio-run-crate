"""Tests for the RunManifest data model."""

from __future__ import annotations

import datetime

import pytest
from pydantic import ValidationError

from bio_run_crate.models import RunManifest


def _valid_data() -> dict[str, object]:
    return {
        "schema_version": "0.1",
        "run_id": "run-0001",
        "title": "Synthetic run",
        "modality": "genomics",
        "created": "2026-01-15",
        "pipeline": {"name": "synthetic-pipeline", "version": "1.0.0"},
        "authors": [{"name": "A. Researcher"}],
    }


def test_valid_data_constructs_manifest() -> None:
    manifest = RunManifest(**_valid_data())
    assert manifest.run_id == "run-0001"
    assert manifest.created == datetime.date(2026, 1, 15)
    assert manifest.pipeline.version == "1.0.0"
    assert manifest.authors[0].name == "A. Researcher"


def test_unknown_key_is_rejected() -> None:
    data = _valid_data()
    data["unexpected"] = "value"
    with pytest.raises(ValidationError):
        RunManifest(**data)


def test_missing_required_field_is_rejected() -> None:
    data = _valid_data()
    del data["run_id"]
    with pytest.raises(ValidationError):
        RunManifest(**data)
