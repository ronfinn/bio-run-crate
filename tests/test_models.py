"""Tests for the RunManifest data model."""

from __future__ import annotations

import datetime

import pytest
from pydantic import ValidationError

from bio_run_crate.models import RunManifest


def _valid_data() -> dict[str, object]:
    return {
        "manifest_version": "0.1",
        "run_id": "run-001",
        "project": {
            "id": "project-001",
            "title": "Synthetic project",
        },
        "dataset": {
            "id": "dataset-001",
            "title": "Synthetic dataset",
            "created": "2026-01-15",
        },
        "biological_context": {
            "organism": {
                "scientific_name": "Homo sapiens",
                "taxon_id": "NCBI:txid9606",
            },
            "tissue": {"name": "liver", "ontology_id": "UBERON:0002107"},
        },
        "assay": {"type": "synthetic-rna-seq"},
        "workflow": {"name": "synthetic-workflow", "version": "1.0.0"},
        "inputs": [
            {
                "id": "input-001",
                "path": "inputs/reads.fastq.gz",
                "role": "primary_input",
            }
        ],
        "outputs": [
            {"id": "output-001", "path": "outputs/counts.tsv", "role": "result_table"}
        ],
    }


def test_valid_data_constructs_manifest() -> None:
    manifest = RunManifest(**_valid_data())
    assert manifest.run_id == "run-001"
    assert manifest.project.id == "project-001"
    assert manifest.dataset.created == datetime.date(2026, 1, 15)
    assert manifest.biological_context.organism.scientific_name == "Homo sapiens"
    assert manifest.biological_context.tissue is not None
    assert manifest.workflow.version == "1.0.0"
    assert manifest.inputs[0].path == "inputs/reads.fastq.gz"
    assert manifest.outputs[0].id == "output-001"


def test_tissue_is_optional() -> None:
    data = _valid_data()
    del data["biological_context"]["organism"]["taxon_id"]  # type: ignore[index]
    data["biological_context"] = {  # type: ignore[assignment]
        "organism": {"scientific_name": "Escherichia coli"}
    }
    manifest = RunManifest(**data)
    assert manifest.biological_context.tissue is None


def test_missing_required_field_is_rejected() -> None:
    data = _valid_data()
    del data["workflow"]
    with pytest.raises(ValidationError):
        RunManifest(**data)


def test_missing_nested_required_field_is_rejected() -> None:
    data = _valid_data()
    del data["biological_context"]["organism"]["scientific_name"]  # type: ignore[index]
    with pytest.raises(ValidationError):
        RunManifest(**data)


def test_bad_id_pattern_is_rejected() -> None:
    data = _valid_data()
    data["run_id"] = "0001"
    with pytest.raises(ValidationError):
        RunManifest(**data)


def test_wrong_type_is_rejected() -> None:
    data = _valid_data()
    data["inputs"] = "not-a-list"
    with pytest.raises(ValidationError):
        RunManifest(**data)


def test_unknown_key_is_rejected() -> None:
    data = _valid_data()
    data["unexpected"] = "value"
    with pytest.raises(ValidationError):
        RunManifest(**data)
