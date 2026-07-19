"""Tests for the YAML manifest loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from bio_run_crate.manifest import load_manifest

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "run_manifest.yaml"


def test_load_example_manifest() -> None:
    manifest = load_manifest(EXAMPLE)
    assert manifest.run_id == "run-0001"
    assert manifest.modality == "genomics"
    assert manifest.pipeline.name == "synthetic-pipeline"


def test_non_mapping_top_level_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_manifest(bad)
