"""Tests for the synthetic example manifest library.

`tests/test_cli.py` covers what a user sees at the command line. This module
covers the fixtures themselves: that the valid example still parses, and that
each deliberately defective example fails in the one way it documents — a
structural failure raising :class:`pydantic.ValidationError`, or a semantic
failure producing a specific structured finding.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from bio_run_crate.findings import Severity
from bio_run_crate.manifest import load_manifest
from bio_run_crate.validation import core_rules, validate_manifest

EXAMPLES = Path(__file__).resolve().parent.parent / "examples" / "synthetic"

#: Every example that fails Pydantic's structural validation, with the field
#: location and error type its primary defect is expected to produce.
STRUCTURAL_FAILURES = [
    ("missing-required-field-run.yaml", "workflow.version", "missing"),
    ("wrong-field-type-run.yaml", "inputs", "list_type"),
]


def test_valid_example_parses_and_has_no_error_findings() -> None:
    result = validate_manifest(load_manifest(EXAMPLES / "valid-run.yaml"))
    assert not result.has_errors


@pytest.mark.parametrize(("filename", "location", "error_type"), STRUCTURAL_FAILURES)
def test_structural_example_fails_with_its_documented_error(
    filename: str, location: str, error_type: str
) -> None:
    with pytest.raises(ValidationError) as raised:
        load_manifest(EXAMPLES / filename)
    reported = {
        (".".join(str(part) for part in item["loc"]), item["type"])
        for item in raised.value.errors()
    }
    assert (location, error_type) in reported
    # Each of these fixtures demonstrates exactly one defect.
    assert len(reported) == 1


def test_targeted_examples_use_only_synthetic_public_safe_values() -> None:
    """Each targeted fixture stays anchored to `example.org` and invented names."""
    filenames = [filename for filename, _, _ in STRUCTURAL_FAILURES]
    for filename in [*filenames, "duplicate-output-id-run.yaml"]:
        text = (EXAMPLES / filename).read_text(encoding="utf-8")
        assert "example.org" in text
        assert "synthetic" in text
        assert "http://" not in text


def test_duplicate_output_id_example_emits_only_core_001() -> None:
    manifest = load_manifest(EXAMPLES / "duplicate-output-id-run.yaml")
    result = validate_manifest(manifest)
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.rule_id == core_rules.DUPLICATE_RESOURCE_ID
    assert finding.severity is Severity.ERROR
    assert finding.location.path == "outputs[1].id"
    assert result.has_errors
