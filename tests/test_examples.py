"""Tests for the synthetic example manifest library.

`tests/test_cli.py` covers what a user sees at the command line. This module
covers the fixtures themselves: that the valid example still parses, and that
each deliberately defective example fails in the one way it documents — a
structural failure raising :class:`pydantic.ValidationError`, or a semantic
failure producing a specific structured finding.
"""

from __future__ import annotations

import re
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


def test_targeted_examples_keep_run_specific_values_synthetic() -> None:
    """Each targeted fixture keeps its *run-specific* values synthetic.

    Only run-scoped data is covered: identifiers, paths and URLs. Biological
    context is deliberately out of scope — the fixtures use real public
    reference terminology and ontology identifiers (`Homo sapiens`,
    `NCBI:txid9606`, `UBERON:0002107`), which are shared vocabulary rather than
    data about anyone, and which must not be replaced with fabricated values.

    This is a lightweight anchor on the fixtures, not a sensitive-data scanner.
    """
    filenames = [filename for filename, _, _ in STRUCTURAL_FAILURES]
    for filename in [*filenames, "duplicate-output-id-run.yaml"]:
        text = (EXAMPLES / filename).read_text(encoding="utf-8")
        # Synthetic run-scoped identifiers, matching the model's ID patterns.
        assert re.search(r"^run_id: run-\d{3,}$", text, re.MULTILINE)
        assert re.search(r"^  id: project-\d{3,}$", text, re.MULTILINE)
        assert re.search(r"^  id: dataset-\d{3,}$", text, re.MULTILINE)
        assert re.search(r"^  - id: output-\d{3,}$", text, re.MULTILINE)
        # Every URL is an `example.org` placeholder, over HTTPS.
        urls = re.findall(r"https?://\S+", text)
        assert urls
        assert all(url.startswith("https://example.org/") for url in urls)


def test_duplicate_output_id_example_emits_only_core_001() -> None:
    manifest = load_manifest(EXAMPLES / "duplicate-output-id-run.yaml")
    result = validate_manifest(manifest)
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.rule_id == core_rules.DUPLICATE_RESOURCE_ID
    assert finding.severity is Severity.ERROR
    assert finding.location.path == "outputs[1].id"
    assert result.has_errors
