"""Tests for the JSON validation report.

These exercise the reporter directly, on hand-built findings rather than on the
output of the rule engine, so that the report's contract can fail independently
of any rule's wording. The CLI end of the same contract lives in
``tests/test_cli.py``.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import ValidationError

from bio_run_crate.findings import Finding, Location, Severity, ValidationResult
from bio_run_crate.manifest import load_manifest
from bio_run_crate.reporting import (
    JSON_REPORT_SCHEMA_VERSION,
    JsonReport,
    SeveritySummary,
    build_json_report,
    render_json_report,
)
from tests.test_cli import VALID

ERROR_FINDING = Finding(
    rule_id="CORE-001",
    severity=Severity.ERROR,
    message="Resource identifier 'output-001' is used more than once in outputs.",
    location=Location(path="outputs[1].id"),
)
WARNING_FINDING = Finding(
    rule_id="CORE-003",
    severity=Severity.WARNING,
    message="Output 'output-002' has no checksum.",
    location=Location(path="outputs[1].checksum"),
)
INFO_FINDING = Finding(
    rule_id="CORE-900",
    severity=Severity.INFO,
    message="Nothing to see here.",
    location=Location(path="inputs[0].role"),
)


def _report(*findings: Finding) -> JsonReport:
    """Build a report for ``run-001`` from ``findings``, without touching disk."""
    return JsonReport(
        run_id="run-001",
        summary=SeveritySummary.from_result(ValidationResult.from_findings(findings)),
        findings=ValidationResult.from_findings(findings).findings,
    )


def _rendered(*findings: Finding) -> dict[str, Any]:
    """Render a report for ``findings`` and parse it back, as a consumer would."""
    parsed: dict[str, Any] = json.loads(render_json_report(_report(*findings)))
    return parsed


# --- Report structure -------------------------------------------------------


def test_report_has_exactly_the_documented_top_level_keys() -> None:
    document = _rendered(WARNING_FINDING)
    assert list(document) == ["schema_version", "run_id", "summary", "findings"]


def test_schema_version_is_the_stable_report_format_version() -> None:
    assert JSON_REPORT_SCHEMA_VERSION == "1"
    assert _rendered()["schema_version"] == "1"


def test_run_id_identifies_the_validated_run() -> None:
    assert _rendered()["run_id"] == "run-001"


def test_summary_always_carries_all_three_severities_including_zeroes() -> None:
    summary = _rendered(WARNING_FINDING)["summary"]
    assert summary == {"ERROR": 0, "WARNING": 1, "INFO": 0}


def test_summary_key_order_is_most_serious_first() -> None:
    assert list(_rendered()["summary"]) == ["ERROR", "WARNING", "INFO"]


def test_no_findings_gives_an_empty_list_and_an_all_zero_summary() -> None:
    document = _rendered()
    assert document["findings"] == []
    assert document["summary"] == {"ERROR": 0, "WARNING": 0, "INFO": 0}


def test_a_finding_carries_rule_id_severity_message_and_nested_location() -> None:
    (finding,) = _rendered(WARNING_FINDING)["findings"]
    assert list(finding) == ["rule_id", "severity", "message", "location"]
    assert finding["rule_id"] == "CORE-003"
    assert finding["severity"] == "WARNING"
    assert finding["message"] == "Output 'output-002' has no checksum."
    assert finding["location"] == {"path": "outputs[1].checksum"}


def test_severity_serialises_as_its_plain_name_not_a_number_or_object() -> None:
    document = _rendered(ERROR_FINDING, INFO_FINDING)
    severities = [f["severity"] for f in document["findings"]]
    assert severities == ["ERROR", "INFO"]


def test_a_warning_only_result_still_produces_a_full_report() -> None:
    document = _rendered(WARNING_FINDING)
    assert document["summary"]["ERROR"] == 0
    assert len(document["findings"]) == 1


def test_an_error_result_is_reported_like_any_other_finding() -> None:
    document = _rendered(ERROR_FINDING)
    assert document["summary"] == {"ERROR": 1, "WARNING": 0, "INFO": 0}
    assert document["findings"][0]["rule_id"] == "CORE-001"


def test_multiple_findings_are_all_present_and_counted() -> None:
    document = _rendered(ERROR_FINDING, WARNING_FINDING, INFO_FINDING)
    assert document["summary"] == {"ERROR": 1, "WARNING": 1, "INFO": 1}
    assert [f["rule_id"] for f in document["findings"]] == [
        "CORE-001",
        "CORE-003",
        "CORE-900",
    ]


# --- Construction contract --------------------------------------------------


def test_build_json_report_reads_the_run_id_from_the_manifest() -> None:
    run = load_manifest(VALID)
    report = build_json_report(run, ValidationResult.from_findings([WARNING_FINDING]))
    assert report.run_id == run.run_id
    assert report.summary.WARNING == 1


def test_building_a_report_does_not_mutate_the_validation_result() -> None:
    result = ValidationResult.from_findings([WARNING_FINDING, ERROR_FINDING])
    before = result.model_copy(deep=True)
    build_json_report(load_manifest(VALID), result)
    assert result == before


def test_report_models_are_frozen_and_reject_unknown_fields() -> None:
    report = _report(WARNING_FINDING)
    with pytest.raises(ValidationError):
        report.run_id = "run-002"  # type: ignore[misc]
    with pytest.raises(ValidationError):
        JsonReport(
            run_id="run-001",
            summary=SeveritySummary(ERROR=0, WARNING=0, INFO=0),
            generated_at="2026-01-01",  # type: ignore[call-arg]
        )


# --- Determinism ------------------------------------------------------------


def test_the_same_findings_in_a_different_order_render_identically() -> None:
    one = render_json_report(_report(ERROR_FINDING, WARNING_FINDING, INFO_FINDING))
    other = render_json_report(_report(INFO_FINDING, ERROR_FINDING, WARNING_FINDING))
    assert one == other


def test_rendering_the_same_report_twice_is_byte_identical() -> None:
    report = _report(ERROR_FINDING, WARNING_FINDING)
    first = render_json_report(report).encode("utf-8")
    assert first == render_json_report(report).encode("utf-8")


def test_findings_stay_in_canonical_order_errors_before_warnings_before_info() -> None:
    document = _rendered(INFO_FINDING, WARNING_FINDING, ERROR_FINDING)
    assert [f["severity"] for f in document["findings"]] == ["ERROR", "WARNING", "INFO"]


def test_serialised_text_is_exactly_the_documented_formatting() -> None:
    """The full byte-for-byte contract: keys, order, indentation, final newline."""
    assert render_json_report(_report(WARNING_FINDING)) == (
        "{\n"
        '  "schema_version": "1",\n'
        '  "run_id": "run-001",\n'
        '  "summary": {\n'
        '    "ERROR": 0,\n'
        '    "WARNING": 1,\n'
        '    "INFO": 0\n'
        "  },\n"
        '  "findings": [\n'
        "    {\n"
        '      "rule_id": "CORE-003",\n'
        '      "severity": "WARNING",\n'
        '      "message": "Output \'output-002\' has no checksum.",\n'
        '      "location": {\n'
        '        "path": "outputs[1].checksum"\n'
        "      }\n"
        "    }\n"
        "  ]\n"
        "}\n"
    )


def test_output_ends_with_exactly_one_newline_and_has_no_trailing_whitespace() -> None:
    text = render_json_report(_report(ERROR_FINDING))
    assert text.endswith("}\n")
    assert not text.endswith("}\n\n")
    assert not any(line != line.rstrip() for line in text.splitlines())
