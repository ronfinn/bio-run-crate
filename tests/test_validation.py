"""Tests for the rule abstraction, the core rule registry, and the engine."""

from __future__ import annotations

import copy
import re

import pytest

from bio_run_crate.findings import (
    CORE_NAMESPACE,
    Finding,
    Location,
    Severity,
    is_valid_rule_id,
)
from bio_run_crate.models import RunManifest
from bio_run_crate.validation import (
    CORE_REGISTRY,
    CORE_RULES,
    RETIRED_CORE_RULE_IDS,
    Rule,
    RuleRegistry,
    core_rules,
    validate_manifest,
)

CORE_RULE_ID_PATTERN = re.compile(r"^CORE-\d{3,}$")


def _manifest(**overrides: object) -> RunManifest:
    """Build a clean synthetic manifest, with optional field overrides."""
    data: dict[str, object] = {
        "manifest_version": "0.1",
        "run_id": "run-001",
        "project": {"id": "project-001", "title": "Synthetic project"},
        "dataset": {"id": "dataset-001", "title": "Synthetic dataset"},
        "biological_context": {"organism": {"scientific_name": "Homo sapiens"}},
        "assay": {"type": "synthetic-assay"},
        "workflow": {"name": "synthetic-workflow", "version": "1.0.0"},
        "inputs": [
            {"id": "input-001", "path": "inputs/a.txt", "role": "primary_input"}
        ],
        "outputs": [
            {
                "id": "output-001",
                "path": "outputs/a.tsv",
                "role": "result_table",
                "checksum": "sha256:" + "0" * 63 + "1",
            }
        ],
    }
    data.update(overrides)
    return RunManifest(**data)  # type: ignore[arg-type]


def _always(rule_id: str, severity: Severity) -> Rule:
    """A test-only rule that always emits exactly one finding."""
    return Rule(
        rule_id=rule_id,
        severity=severity,
        description=f"Always emits one {severity} finding.",
        check=lambda _manifest: (
            Finding(rule_id=rule_id, severity=severity, message=f"{rule_id} fired."),
        ),
    )


#: A throwaway registry covering all three severities. Deliberately *not* part
#: of the shipped core rule set: severity coverage is a property of the engine
#: and of issue #5's findings model, not a reason to invent core rules.
_TEST_REGISTRY = RuleRegistry(
    [
        _always("TEST-001", Severity.ERROR),
        _always("TEST-002", Severity.WARNING),
        _always("TEST-003", Severity.INFO),
    ],
    namespace="TEST",
)


# --- Registry and rule metadata ---------------------------------------------


def test_every_core_rule_has_a_valid_core_identifier() -> None:
    for rule in CORE_RULES:
        assert is_valid_rule_id(rule.rule_id)
        assert CORE_RULE_ID_PATTERN.match(rule.rule_id)
        assert rule.rule_id.split("-", 1)[0] == CORE_NAMESPACE


def test_core_rule_identifiers_are_unique() -> None:
    ids = [rule.rule_id for rule in CORE_RULES]
    assert len(ids) == len(set(ids))
    assert CORE_REGISTRY.rule_ids == set(ids)


def test_every_core_rule_has_a_description() -> None:
    for rule in CORE_RULES:
        assert rule.description


def test_registry_rejects_duplicate_identifiers() -> None:
    rule = CORE_RULES[0]
    with pytest.raises(ValueError, match="Duplicate rule identifier"):
        RuleRegistry([rule, rule])


def test_registry_rejects_a_reused_retired_identifier() -> None:
    rule = CORE_RULES[0]
    with pytest.raises(ValueError, match="was retired"):
        RuleRegistry([rule], retired_rule_ids={rule.rule_id})


def test_no_active_core_rule_reuses_a_retired_identifier() -> None:
    assert CORE_REGISTRY.rule_ids.isdisjoint(RETIRED_CORE_RULE_IDS)


def test_core_registry_is_pinned_to_the_core_namespace() -> None:
    assert CORE_REGISTRY.namespace == CORE_NAMESPACE


def test_core_registry_rejects_a_rule_from_another_namespace() -> None:
    """A profile rule cannot be added to the core rule set by mistake."""
    profile_rule = _always("SEQ-001", Severity.WARNING)
    with pytest.raises(ValueError, match="not in the CORE namespace"):
        RuleRegistry([*CORE_RULES, profile_rule], namespace=CORE_NAMESPACE)


def test_a_registry_can_pin_a_profile_namespace() -> None:
    """The Rule/registry machinery is not core-specific (ADR-0003)."""
    registry = RuleRegistry([_always("SEQ-001", Severity.WARNING)], namespace="SEQ")
    assert registry.namespace == "SEQ"
    assert registry.get("SEQ-001").namespace == "SEQ"
    result = validate_manifest(_manifest(), registry=registry)
    assert [f.rule_id for f in result.findings] == ["SEQ-001"]


def test_rule_rejects_a_malformed_identifier() -> None:
    with pytest.raises(ValueError, match="Invalid rule identifier"):
        Rule(
            rule_id="core-1",
            severity=Severity.INFO,
            description="Malformed.",
            check=lambda _manifest: (),
        )


def test_rule_rejects_a_finding_from_another_rule() -> None:
    rule = Rule(
        rule_id="CORE-901",
        severity=Severity.INFO,
        description="Misattributes its finding.",
        check=lambda _manifest: (
            Finding(rule_id="CORE-902", severity=Severity.INFO, message="x"),
        ),
    )
    with pytest.raises(ValueError, match="attributed to"):
        rule.apply(_manifest())


def test_rule_rejects_a_severity_it_did_not_declare() -> None:
    rule = Rule(
        rule_id="CORE-903",
        severity=Severity.INFO,
        description="Emits the wrong severity.",
        check=lambda _manifest: (
            Finding(rule_id="CORE-903", severity=Severity.ERROR, message="x"),
        ),
    )
    with pytest.raises(ValueError, match="declares severity"):
        rule.apply(_manifest())


def test_every_core_rule_emits_structured_findings_of_its_declared_severity() -> None:
    """Each rule's findings are Finding objects carrying its own ID/severity."""
    manifest = _manifest(
        outputs=[
            {"id": "output-001", "path": "outputs/a.tsv", "role": "result_table"},
            {"id": "output-001", "path": "outputs/b.tsv", "role": "qc_report"},
        ],
    )
    emitted = {
        rule.rule_id: findings
        for rule in CORE_RULES
        if (findings := rule.apply(manifest))
    }
    # This manifest is built so that every core rule fires at least once.
    assert set(emitted) == {rule.rule_id for rule in CORE_RULES}
    for rule in CORE_RULES:
        for finding in emitted[rule.rule_id]:
            assert isinstance(finding, Finding)
            assert finding.rule_id == rule.rule_id
            assert finding.severity is rule.severity
            assert finding.message


# --- Individual core rules ---------------------------------------------------


def test_clean_manifest_produces_no_findings() -> None:
    assert validate_manifest(_manifest()).findings == ()


def test_duplicate_resource_id_is_an_error_at_the_repeated_entry() -> None:
    manifest = _manifest(
        inputs=[
            {"id": "input-001", "path": "inputs/a.txt", "role": "primary_input"},
            {"id": "input-001", "path": "inputs/b.txt", "role": "primary_input"},
        ]
    )
    (finding,) = validate_manifest(manifest).findings
    assert finding.rule_id == core_rules.DUPLICATE_RESOURCE_ID
    assert finding.severity is Severity.ERROR
    assert finding.location == Location(path="inputs[1].id")
    assert "input-001" in finding.message


def test_duplicate_resource_id_reports_every_repeat_occurrence() -> None:
    manifest = _manifest(
        inputs=[
            {"id": "input-001", "path": "inputs/a.txt", "role": "primary_input"},
            {"id": "input-001", "path": "inputs/b.txt", "role": "primary_input"},
            {"id": "input-001", "path": "inputs/c.txt", "role": "primary_input"},
        ]
    )
    findings = validate_manifest(manifest).findings
    assert [f.location.path for f in findings] == ["inputs[1].id", "inputs[2].id"]
    assert {f.severity for f in findings} == {Severity.ERROR}


def test_a_path_shared_by_two_resources_is_not_a_finding() -> None:
    """The model permits one file described under two roles; not a rule."""
    manifest = _manifest(
        outputs=[
            {
                "id": "output-001",
                "path": "outputs/a.tsv",
                "role": "result_table",
                "checksum": "sha256:01",
            },
            {
                "id": "output-002",
                "path": "outputs/a.tsv",
                "role": "qc_report",
                "checksum": "sha256:02",
            },
        ]
    )
    assert validate_manifest(manifest).findings == ()


def test_output_without_checksum_is_a_warning() -> None:
    manifest = _manifest(
        outputs=[{"id": "output-001", "path": "outputs/a.tsv", "role": "result_table"}]
    )
    (finding,) = validate_manifest(manifest).findings
    assert finding.rule_id == core_rules.OUTPUT_WITHOUT_CHECKSUM
    assert finding.severity is Severity.WARNING
    assert finding.location == Location(path="outputs[0].checksum")


def test_input_without_checksum_produces_no_finding() -> None:
    """The checksum recommendation applies to outputs only (data model §A.7)."""
    manifest = _manifest(
        inputs=[{"id": "input-001", "path": "inputs/a.txt", "role": "primary_input"}]
    )
    assert validate_manifest(manifest).findings == ()


def test_empty_collections_produce_no_findings() -> None:
    """§A.1 permits empty inputs and outputs; a permitted state is not flagged."""
    assert validate_manifest(_manifest(inputs=[], outputs=[])).findings == ()


# --- Engine behaviour --------------------------------------------------------


def test_engine_collects_findings_from_multiple_rules() -> None:
    manifest = _manifest(
        outputs=[
            {"id": "output-001", "path": "outputs/a.tsv", "role": "result_table"},
            {"id": "output-001", "path": "outputs/b.tsv", "role": "qc_report"},
        ]
    )
    result = validate_manifest(manifest)
    # Canonical order: ERROR first, then WARNINGs by location path.
    assert [(f.rule_id, f.location.path) for f in result.findings] == [
        (core_rules.DUPLICATE_RESOURCE_ID, "outputs[1].id"),
        (core_rules.OUTPUT_WITHOUT_CHECKSUM, "outputs[0].checksum"),
        (core_rules.OUTPUT_WITHOUT_CHECKSUM, "outputs[1].checksum"),
    ]
    assert result.has_errors
    assert result.counts() == {
        Severity.ERROR: 1,
        Severity.WARNING: 2,
        Severity.INFO: 0,
    }


def test_engine_reports_all_three_severities_at_once() -> None:
    """Mixed-severity handling is engine behaviour, tested with test-only rules.

    The production core rule set has no INFO rule, and one must not be invented
    to make this case reachable; a throwaway registry exercises it instead.
    """
    result = validate_manifest(_manifest(), registry=_TEST_REGISTRY)
    assert [f.rule_id for f in result.findings] == ["TEST-001", "TEST-002", "TEST-003"]
    assert [f.severity for f in result.findings] == [
        Severity.ERROR,
        Severity.WARNING,
        Severity.INFO,
    ]
    assert result.counts() == {
        Severity.ERROR: 1,
        Severity.WARNING: 1,
        Severity.INFO: 1,
    }


def test_engine_output_is_deterministic() -> None:
    manifest = _manifest(
        outputs=[{"id": "output-001", "path": "outputs/a.tsv", "role": "result_table"}]
    )
    first = validate_manifest(manifest)
    second = validate_manifest(manifest)
    assert first == second
    assert first.model_dump_json() == second.model_dump_json()


def test_rule_execution_order_cannot_affect_finding_order() -> None:
    """Reversing the registry changes execution order, never the result."""
    manifest = _manifest(
        outputs=[
            {"id": "output-001", "path": "outputs/a.tsv", "role": "result_table"},
            {"id": "output-001", "path": "outputs/b.tsv", "role": "qc_report"},
        ],
    )
    forward = validate_manifest(manifest, registry=CORE_REGISTRY)
    reversed_registry = RuleRegistry(reversed(CORE_RULES))
    backward = validate_manifest(manifest, registry=reversed_registry)
    assert [rule.rule_id for rule in reversed_registry] != [
        rule.rule_id for rule in CORE_REGISTRY
    ]
    assert forward.findings == backward.findings


def test_engine_does_not_mutate_the_manifest() -> None:
    manifest = _manifest(
        outputs=[{"id": "output-001", "path": "outputs/a.tsv", "role": "result_table"}]
    )
    before = copy.deepcopy(manifest)
    validate_manifest(manifest)
    assert manifest == before


def test_engine_accepts_an_alternative_registry() -> None:
    only_checksums = RuleRegistry(
        [CORE_REGISTRY.get(core_rules.OUTPUT_WITHOUT_CHECKSUM)]
    )
    manifest = _manifest(
        outputs=[{"id": "output-001", "path": "outputs/a.tsv", "role": "result_table"}],
    )
    result = validate_manifest(manifest, registry=only_checksums)
    assert [f.rule_id for f in result.findings] == [core_rules.OUTPUT_WITHOUT_CHECKSUM]
