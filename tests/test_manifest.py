"""Tests for the YAML manifest loader."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from bio_run_crate.manifest import load_manifest

EXAMPLES = Path(__file__).resolve().parent.parent / "examples" / "synthetic"
VALID = EXAMPLES / "valid-run.yaml"


def test_load_valid_manifest() -> None:
    manifest = load_manifest(VALID)
    assert manifest.run_id == "run-001"
    assert manifest.project.id == "project-001"
    assert manifest.workflow.name == "synthetic-rnaseq-workflow"
    assert len(manifest.outputs) == 2


def test_malformed_yaml_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("key: [unclosed\n", encoding="utf-8")
    with pytest.raises(yaml.YAMLError):
        load_manifest(bad)


def test_missing_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist.yaml"
    with pytest.raises(FileNotFoundError):
        load_manifest(missing)


def test_non_mapping_top_level_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_manifest(bad)
