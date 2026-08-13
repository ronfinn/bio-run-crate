"""The validation engine: apply a rule set to a manifest, collect findings.

The engine is deliberately trivial, and that is the point — all judgement lives
in the rules, all ordering lives in
:class:`~bio_run_crate.findings.ValidationResult`, and all presentation lives in
the CLI. The engine only sequences them.

It runs *every* registered rule; a rule that produces findings does not stop the
rules after it, so one run reports everything wrong with a manifest rather than
only the first problem.
"""

from __future__ import annotations

from bio_run_crate.findings import Finding, ValidationResult
from bio_run_crate.models import RunManifest
from bio_run_crate.validation.core_rules import CORE_REGISTRY
from bio_run_crate.validation.registry import RuleRegistry


def validate_manifest(
    manifest: RunManifest,
    *,
    registry: RuleRegistry = CORE_REGISTRY,
) -> ValidationResult:
    """Apply every rule in ``registry`` to ``manifest`` and return the result.

    The manifest must already have been parsed successfully — structural and
    schema problems are Pydantic's job and never reach this function.

    The call is deterministic (identical input yields an identical result),
    performs no I/O or network access, and does not mutate ``manifest``. The
    returned :class:`~bio_run_crate.findings.ValidationResult` holds its
    findings in canonical order, so the order rules ran in is not observable.

    Args:
        manifest: A successfully parsed manifest.
        registry: The rules to apply. Defaults to the core rule set.
    """
    findings: list[Finding] = []
    for rule in registry:
        findings.extend(rule.apply(manifest))
    return ValidationResult.from_findings(findings)
