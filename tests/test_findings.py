"""Tests for the structured findings model."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from bio_run_crate.findings import (
    CORE_NAMESPACE,
    ROOT_PATH,
    Finding,
    Location,
    Severity,
    ValidationResult,
    is_valid_rule_id,
)


def _finding(
    rule_id: str = "CORE-001",
    severity: Severity = Severity.ERROR,
    message: str = "Synthetic finding.",
    path: str = ROOT_PATH,
) -> Finding:
    return Finding(
        rule_id=rule_id,
        severity=severity,
        message=message,
        location=Location(path=path),
    )


# --- construction ---------------------------------------------------------


def test_valid_finding_constructs() -> None:
    finding = _finding(path="inputs[0].checksum")
    assert finding.rule_id == "CORE-001"
    assert finding.severity is Severity.ERROR
    assert finding.message == "Synthetic finding."
    assert finding.location.path == "inputs[0].checksum"
    assert finding.namespace == CORE_NAMESPACE


def test_location_defaults_to_root() -> None:
    finding = Finding(rule_id="CORE-002", severity=Severity.INFO, message="Note.")
    assert finding.location == Location.root()
    assert finding.location.path == ROOT_PATH


def test_empty_message_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _finding(message="")


def test_unknown_field_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Finding(
            rule_id="CORE-001",
            severity=Severity.ERROR,
            message="Synthetic finding.",
            hint="not a field",  # type: ignore[call-arg]
        )


# --- severity -------------------------------------------------------------


def test_exactly_three_severities_exist() -> None:
    assert [member.value for member in Severity] == ["ERROR", "WARNING", "INFO"]


@pytest.mark.parametrize("value", ["ERROR", "WARNING", "INFO"])
def test_severity_accepts_its_own_names(value: str) -> None:
    assert Finding(rule_id="CORE-001", severity=value, message="m").severity == value  # type: ignore[arg-type]


@pytest.mark.parametrize("value", ["error", "CRITICAL", "DEBUG", "", "FATAL"])
def test_severity_rejects_anything_else(value: str) -> None:
    with pytest.raises(ValidationError):
        Finding(rule_id="CORE-001", severity=value, message="m")  # type: ignore[arg-type]


# --- rule IDs -------------------------------------------------------------


@pytest.mark.parametrize("rule_id", ["CORE-001", "CORE-9999", "SEQ-014", "MS2-003"])
def test_valid_rule_ids_are_accepted(rule_id: str) -> None:
    assert is_valid_rule_id(rule_id)
    assert _finding(rule_id=rule_id).rule_id == rule_id


@pytest.mark.parametrize(
    "rule_id",
    [
        "core-001",  # namespace must be uppercase
        "CORE-1",  # number must be at least three digits
        "CORE001",  # separator required
        "C-001",  # namespace too short
        "1CORE-001",  # namespace must start with a letter
        "CORE-001-A",  # trailing segment
        "CORE_001",  # wrong separator
        "",
    ],
)
def test_invalid_rule_ids_are_rejected(rule_id: str) -> None:
    assert not is_valid_rule_id(rule_id)
    with pytest.raises(ValidationError):
        _finding(rule_id=rule_id)


def test_namespace_is_derived_from_the_rule_id() -> None:
    assert _finding(rule_id="SEQ-014").namespace == "SEQ"


# --- locations ------------------------------------------------------------


def test_from_parts_renders_fields_and_indices() -> None:
    assert Location.from_parts("inputs", 0, "checksum").path == "inputs[0].checksum"
    assert Location.from_parts("workflow", "version").path == "workflow.version"
    assert Location.from_parts().path == ROOT_PATH
    assert str(Location.from_parts("run_id")) == "run_id"


@pytest.mark.parametrize(
    "parts",
    [(0, "inputs"), ("inputs", -1), ("inputs", "", "id")],
    ids=["leading-index", "negative-index", "empty-field"],
)
def test_from_parts_rejects_malformed_parts(parts: tuple[str | int, ...]) -> None:
    with pytest.raises(ValueError):
        Location.from_parts(*parts)


def test_empty_location_path_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Location(path="")


# --- immutability ---------------------------------------------------------


def test_models_are_frozen() -> None:
    finding = _finding()
    result = ValidationResult.from_findings([finding])
    with pytest.raises(ValidationError):
        finding.message = "changed"
    with pytest.raises(ValidationError):
        finding.location.path = "changed"
    with pytest.raises(ValidationError):
        result.findings = ()


# --- ordering -------------------------------------------------------------


def _unordered_findings() -> list[Finding]:
    return [
        _finding("CORE-003", Severity.INFO, "Info at root."),
        _finding("CORE-002", Severity.ERROR, "Second error.", "outputs[0].path"),
        _finding("CORE-001", Severity.WARNING, "A warning.", "inputs[0].checksum"),
        _finding("CORE-002", Severity.ERROR, "First error.", "inputs[0].path"),
        _finding("CORE-004", Severity.ERROR, "Zzz message.", "inputs[0].path"),
    ]


def test_findings_are_ordered_by_severity_then_location_rule_and_message() -> None:
    result = ValidationResult.from_findings(_unordered_findings())
    assert [(f.severity, f.location.path, f.rule_id) for f in result.findings] == [
        (Severity.ERROR, "inputs[0].path", "CORE-002"),
        (Severity.ERROR, "inputs[0].path", "CORE-004"),
        (Severity.ERROR, "outputs[0].path", "CORE-002"),
        (Severity.WARNING, "inputs[0].checksum", "CORE-001"),
        (Severity.INFO, ROOT_PATH, "CORE-003"),
    ]


def test_ordering_is_independent_of_input_order() -> None:
    findings = _unordered_findings()
    expected = ValidationResult.from_findings(findings).findings
    for rotation in range(len(findings)):
        rotated = findings[rotation:] + findings[:rotation]
        assert ValidationResult.from_findings(rotated).findings == expected
    assert ValidationResult.from_findings(reversed(findings)).findings == expected


def test_ties_are_broken_by_message() -> None:
    first = _finding("CORE-001", Severity.ERROR, "aaa", "run_id")
    second = _finding("CORE-001", Severity.ERROR, "bbb", "run_id")
    assert ValidationResult.from_findings([second, first]).findings == (first, second)


def _shuffles(findings: list[Finding]) -> list[list[Finding]]:
    """Deterministic reorderings of ``findings``: every rotation, plus reversal."""
    rotations = [findings[i:] + findings[:i] for i in range(len(findings))]
    return [*rotations, list(reversed(findings))]


def test_direct_construction_canonicalises_order() -> None:
    findings = _unordered_findings()
    expected = ValidationResult.from_findings(findings).findings
    for reordered in _shuffles(findings):
        result = ValidationResult(findings=tuple(reordered))
        assert result.findings == expected
        assert result == ValidationResult(findings=tuple(findings))


def test_direct_construction_produces_identical_json_for_any_input_order() -> None:
    payloads = {
        ValidationResult(findings=tuple(reordered)).model_dump_json()
        for reordered in _shuffles(_unordered_findings())
    }
    assert len(payloads) == 1


def test_model_validate_canonicalises_order() -> None:
    findings = _unordered_findings()
    expected = ValidationResult.from_findings(findings).findings
    for reordered in _shuffles(findings):
        payload = {"findings": [f.model_dump(mode="json") for f in reordered]}
        assert ValidationResult.model_validate(payload).findings == expected


def test_ordering_does_not_mutate_the_callers_collection() -> None:
    findings = _unordered_findings()
    before = list(findings)
    ValidationResult.from_findings(findings)
    ValidationResult(findings=tuple(findings))
    assert findings == before
    assert findings[0].severity is Severity.INFO  # still unsorted


# --- aggregation ----------------------------------------------------------


def test_empty_result_has_no_findings_and_no_errors() -> None:
    result = ValidationResult.from_findings()
    assert result.findings == ()
    assert not result.has_errors
    assert result.counts() == {Severity.ERROR: 0, Severity.WARNING: 0, Severity.INFO: 0}


def test_counts_and_has_errors_reflect_the_findings() -> None:
    result = ValidationResult.from_findings(_unordered_findings())
    assert result.counts() == {Severity.ERROR: 3, Severity.WARNING: 1, Severity.INFO: 1}
    assert result.has_errors


def test_with_severity_filters_and_preserves_order() -> None:
    result = ValidationResult.from_findings(_unordered_findings())
    errors = result.with_severity(Severity.ERROR)
    assert [f.location.path for f in errors] == [
        "inputs[0].path",
        "inputs[0].path",
        "outputs[0].path",
    ]
    assert result.with_severity(Severity.WARNING)[0].rule_id == "CORE-001"


def test_result_without_errors_reports_no_errors() -> None:
    result = ValidationResult.from_findings(
        [_finding("CORE-003", Severity.INFO, "Just a note.")]
    )
    assert not result.has_errors


# --- JSON serialisation ---------------------------------------------------


def test_finding_serialises_to_plain_json_types() -> None:
    payload = _finding(path="inputs[0].checksum").model_dump(mode="json")
    assert payload == {
        "rule_id": "CORE-001",
        "severity": "ERROR",
        "message": "Synthetic finding.",
        "location": {"path": "inputs[0].checksum"},
    }
    assert json.loads(json.dumps(payload)) == payload


def test_result_json_is_stable_across_input_orders() -> None:
    findings = _unordered_findings()
    first = ValidationResult.from_findings(findings).model_dump_json()
    second = ValidationResult.from_findings(reversed(findings)).model_dump_json()
    assert first == second
    assert json.loads(first)["findings"][0]["severity"] == "ERROR"


def test_result_round_trips_through_json() -> None:
    result = ValidationResult.from_findings(_unordered_findings())
    restored = ValidationResult.model_validate_json(result.model_dump_json())
    assert restored == result
    assert restored.findings == result.findings
    assert restored.model_dump_json() == result.model_dump_json()


def test_deserialising_a_shuffled_payload_restores_canonical_order() -> None:
    """A hand-written or externally reordered payload is canonicalised on read."""
    canonical = ValidationResult.from_findings(_unordered_findings())
    shuffled = {
        "findings": [f.model_dump(mode="json") for f in reversed(_unordered_findings())]
    }
    restored = ValidationResult.model_validate(shuffled)
    assert restored == canonical
    assert restored.model_dump_json() == canonical.model_dump_json()
